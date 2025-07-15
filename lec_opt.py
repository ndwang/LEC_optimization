from subprocess import run
from pmd_beamphysics import ParticleGroup
import numpy as np
from os import remove
import os.path
import hashlib
import json

BASE_PATH = "/home/nw285/temp/lec/"
RELATIVE_PATH = "temp/"

def get_param_id(params: dict) -> str:
    param_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(param_str.encode()).hexdigest()
    
############### tracking functions ###############
def track(input, ID):
    FILENAME = BASE_PATH + RELATIVE_PATH + ID
    
    # Check for duplicate
    if os.path.isfile(f"{FILENAME}.h5"):
        return ParticleGroup(f"{FILENAME}.h5")
        
    commands = f"set global lattice_calc_on = F\n set ele O_CAV phase = {input['phase']}\n set ele O_CAV phase3 = {input['phase3']}\n set ele O_CAV voltage = {input['voltage']}\n set ele O_CAV voltage3 = {input['voltage3']}\n set global lattice_calc_on = T\n set global track_type = beam\n write beam -at H3.END {FILENAME}.h5\n exit"
    f = open(f"{FILENAME}.tao", "w")
    f.write(commands)
    f.close()
    
    run(["tao", "-noplot", "-command", f"call {FILENAME}.tao"])
    if os.path.isfile(f"{FILENAME}.tao"):
        remove(f"{FILENAME}.tao")
    return ParticleGroup(f"{FILENAME}.h5")

############### evaluator functions ###############
def objective_calc(P):
    # Target gamma is 25.4
    target_gamma = 25.4
    mean_gamma = P['mean_gamma']
    gamma_error = ((mean_gamma - target_gamma) / target_gamma) **2
    
    # Get sigma_energy to minimize
    sigma_energy = P['sigma_energy']
    energy_spread = sigma_energy / P["mean_energy"]
    
    return gamma_error, energy_spread, sigma_energy, mean_gamma


############### top level functions ###############
def opt(inputs: dict) -> dict:
    # Generate unique ID for this parameter set
    ID = get_param_id(inputs)
    
    # Track the beam
    P = track(inputs, ID)
    
    # Calculate objectives
    gamma_error, energy_spread, sigma_energy, mean_gamma = objective_calc(P)
    
    return {
        'gamma_error': gamma_error,
        'energy_spread': energy_spread,
        'sigma_energy': sigma_energy,
        'mean_gamma': mean_gamma,
        'n_alive_ratio': P['n_alive']/P['n_particle'],
        'ID': ID
    }


############### test and main ###############
def test(inputs: dict) -> dict:
    return {
        'gamma_error': 0.01,
        'energy_spread': 0.05,
        'sigma_energy': 6e5,
        'mean_gamma': 25.4,
        'n_alive_ratio': 1.0
    }

def main():
    # Test the optimization function
    test_inputs = {
        'phase': 0.0,
        'phase3': 0.5,
        'voltage': 800e3,
        'voltage3': 400e3
    }
    
    print("Testing O_CAV optimization:")
    result = opt(test_inputs)
    print(f"Results: {result}")
    
    # Print optimization objectives
    print(f"\nOptimization objectives:")
    print(f"- Target mean_gamma: 25.4 (current: {result['mean_gamma']:.3f})")
    print(f"- Gamma error: {result['gamma_error']:.6f}")
    print(f"- Sigma energy: {result['sigma_energy']:.6f}")
    print(f"- Particles alive ratio: {result['n_alive_ratio']}")

if __name__=='__main__':
    main()
