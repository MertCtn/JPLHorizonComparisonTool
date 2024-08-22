# JPL Horizon Comparison Tool

This project is a comprehensive tool designed to fetch ephemerides data from the JPL Horizons API and compare it with your own ephemerides calculations stored in separate .dat files. The tool computes differences between datasets, saves the results to files, and generates detailed plots for each dimension (X, Y, Z) as well as the total distance (R). Additionally, it can plot other calculations such as whole system energy and angular momentum. You can also use this code for your own work with your own caulculations. You can plot any two dimensional plot you want.

The code shared in the present GitHub repository arose in support of a personal project [[1]](https://doi.org/10.5281/zenodo.13358550) pursued by my colleague [Cengiz Yıldırım](https://www.linkedin.com/in/cengiz-y%C4%B1ld%C4%B1r%C4%B1m-66202b283/), in the Department of Aerospace Engineering of the Izmir University of Economics. In his project, the positions of the planets are computed by means of the leapfrog method, as illustrated by Richard Feynman in the Lectures on Physics [[2]](https://www.feynmanlectures.caltech.edu/info/). While Cengiz was a student in [Dr. Fabrizio Pinto](https://www.linkedin.com/in/fabrizio-pinto-33b8b3133/)'s class on Spacecraft Design, he became interested in implementing Feynman's concept in Fortran 90 and asked for my help in producing the present code, to access the Horizons Web Application maintained by the NASA/Jet Propulsion Laboratory at Caltech, to download the positions of the objects of interest by means of the available API, and to calculate the differences between Cengiz's calculations and the NASA data. The code Cengiz developed independently is also available on GitHub [[3]](https://github.com/cengizyildirim-aerospace/Fortran-Astro); further information about the historical background of Feynman's method is provided by Fabrizio Pinto in Ref. [[4]](https://www.torrossa.com/en/resources/an/5327302?digital=true#).

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - Fetching Ephemerides Data
  - Calculationg Differences
  - Plotting Data
- [Functions Overview](#functions_overview)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

## Features

- Data Fetching: Retrieve high-precision ephemerides data from the JPL Horizons API for major solar system bodies.

- Data Comparison: Compare fetched data with custom ephemerides calculations using various metrics.

- Automated Request Handling: Automatically splits requests based on API limits to ensure smooth data retrieval.

- Data Visualization: Generates comprehensive plots for positional differences and other calculated metrics like energy and angular momentum.

- Customizable Parameters: Easily adjust time ranges, step sizes, and targeted celestial bodies.

- Error Handling: Robust error checking and informative logging throughout the data processing pipeline.

## Prerequisites

Before using this tool, ensure you have the following installed:

- **Python 3.7 or higher**
- **Python Packages:**
  - `requests`
  - `numpy`
  - `matplotlib`

You can install the required packages using pip:

```bash
pip install requests numpy matplotlib
```

## Installation

1. **Clone The Repository:**

```bash
git clone https://github.com/mertctn/ephemerides-comparison-tool.git
```

2. **Navigate to the Project Directory:**

```bash
cd ephemerides-comparison-tool
```

3. **Install Dependencies:**

```bash
pip install requests numpy matplotlib
```

## Usage

The tool is structured around several core functions that handle data fetching, processing, and visualization. You can use these functions individually or combine them in scripts as needed.

### Fetching Ephemerides Data

Use the fetch_ephemerides function to retrieve data from the JPL Horizons API.
JPL Horizons API will respond in csv format and fetch_ephemerides function will create a file to your working directory.

#### Parameters

- `object_id` : The ID of the celestial body (e.g., '3' for Earth-Moon Barycenter).
- `start_time` : Start date in 'YYYY-MM-DD' format.
- `stop_time` : End date in 'YYYY-MM-DD' format.
- `output_filename` : Desired name for the output CSV file.

#### Example

```python
fetch_ephemerides('3', '2024-02-09', '2025-02-07', 'EarthMoonEphemerides')
```

### Calculating Differences

Use the **calc_ephemerides_diff** function to compute differences between the fetched data and your own calculations.
You need to put your .dat files for each planet into your working directory. It will produce results .dat file and draw plots for each dimension (x,y,z) and radius.

#### Parameters

- `horizons_filename` : Name of the Horizons data CSV file (without extension).
- `input_filename` : Name of your calculations data file (without extension).
- `output_directory` : Directory where results and plots will be saved.

### Plotting Data

Use the **plot_from_file** function to plot various metrics from your data files.
It can be used with any desired .dat file for plotting other calculations.

#### Parameters

- `input_file_name` : Path to the input data file.
- `output_file_name` : Path where the plot image will be saved.
- `x_column_index` : Column index for X-axis data usually 0.
- `y_column_index` : Column index for Y-axis data usually 1.
- `x_label` : Label for the X-axis.
- `y_label` : Label for the Y-axis.

#### Example

```python
plot_from_file('WholeSystemEnergy.dat', 'WholeSystemEnergyPlot.png', 0, 1, 'Time (s)', 'Energy Difference (J)')
```

### Examples

#### Example 1: Fetching and Comparing Earth-Moon Data

```python
# Define time range
start_time = '2024-02-09'
stop_time = '2025-02-07'

# Fetch ephemerides data for Earth-Moon system
fetch_ephemerides('3', start_time, stop_time, 'EarthMoonEphemerides')

# Calculate differences between fetched data and custom calculations
calc_ephemerides_diff('EarthMoonEphemerides', 'EarthMoonPosition', 'EarthMoonResults')

# Plot the whole system energy
plot_from_file('WholeSystemEnergy.dat', 'WholeSystemEnergyPlot.png', 0, 1, 'Time (s)', 'Energy Difference (J)')
```

#### Example 2: Processing Multiple Celestial Bodies

```python
# Define major bodies with their respective IDs
major_bodies = {
    '1': 'Mercury',
    '2': 'Venus',
    '3': 'Earth-Moon',
    '4': 'Mars',
    '5': 'Jupiter',
    '6': 'Saturn',
    '7': 'Uranus',
    '8': 'Neptune',
    '9': 'Pluto',
    '10': 'Sun'
}

# Define time range
start_time = '2024-02-09'
stop_time = '2025-02-07'

# Process each major body
for object_id, name in major_bodies.items():
    output_filename = f"{name}Ephemerides"
    results_directory = f"{name}Results"
    
    # Fetch data
    fetch_ephemerides(object_id, start_time, stop_time, output_filename)
    
    # Calculate differences
    calc_ephemerides_diff(output_filename, f"{name}Position", results_directory)

```

## Contributing

1. Fork the Repository
2. Create a Feature Branch
```bash
git checkout -b feature/YourFeature
```
3. Commit Your Changes
```bash
git commit -m "Add your commit message here"
```
4. Push to the Branch
```bash
git push origin feature/YourFeature
```
5. Open a Pull Request

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/deed.en)

## References

[1] C. Yıldırım 
LINK : 10.5281/zenodo.13358550

[2] R. P. Feynman, R. P. Leighton, and M. Sands,  The Feynman's Lectures on Physics (Caltech, Pasadena, 1963). Vol. 1, Sec. 9-7. LINK: https://www.feynmanlectures.caltech.edu/info/ 

[3]  C. Yıldırım here we shall write Cengiz's Github reference 
LINK: https://github.com/cengizyildirim-aerospace/Fortran-Astro

[4] F. Pinto, "Feynman on “Planetary Motions”," in Atti del XLI Convegno annuale della SISFA, Arezzo, September 6-9, 2021 (Pisa University Press, Pisa, 2022), pp. 128–138.  LINK: https://www.torrossa.com/en/resources/an/5327302?digital=true# 

[5] JPL Horizons https://ssd.jpl.nasa.gov/horizons/

[6] JPL Horizons API Documentation https://ssd-api.jpl.nasa.gov/doc/horizons.html

