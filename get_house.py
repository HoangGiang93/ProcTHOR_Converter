#!/usr/bin/env python3

import argparse
import prior
import json

dataset = prior.load_dataset("procthor-10k")
houses = dataset["train"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto semantic tagging based on object names")
    parser.add_argument("--house", type=str, required=True, help="Input JSON")
    args = parser.parse_args()

    if args.house:
        house_number = int(args.house)
    else:
        print("Enter the house number: ", end="")
        house_number = int(input())

    house = houses[house_number]
    with open(f"house_{house_number}.json", "w") as file:
        json.dump(house, file, indent=4)
    