# PROCTHOR Converter

## Installation

1. Install [Multiverse](https://multiverseframework.readthedocs.io/en/latest/installation.html) excluding ROS

2. Install [procthor](https://github.com/allenai/procthor-10k)

```bash
pip install prior
```

3. Retrive meshes from [ai2thor](https://github.com/allenai/ai2thor)

```bash
sh retrieve_procthor_data.bash
```

## Usage

```bash
sh procthor_to_everything.bash <house_number>
# e.g.
# sh procthor_to_everything.bash 1
```

It will start everything and store the result in a folder in the same directory (e.g. house_1)
