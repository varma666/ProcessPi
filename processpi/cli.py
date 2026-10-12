import time
from tqdm import tqdm

def main():
    print("Launching ProcessPI...")
    for i in tqdm(range(50), desc="Initializing package"):
        time.sleep(0.05)  # simulate loading
    print("ProcessPI ready!")
