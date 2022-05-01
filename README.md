# Instax Photo Converter

## Overview

A while back I was gifted an [Instax SQ 10](https://www.amazon.com/Fujifilm-Instax-Square-Instant-Camera/dp/B06Y66DM52?th=1) digital polaroid camera. I found it a bit too bulky and the photos to be pretty poor quality so I wanted to use it as a polaroid printer. Unfortunately you cannot just load photos onto the microSD card and print them. They need to be square photos with some metadata attached in the form of a CSV file.

So I made this small CLI tool to crop the photos using pygame and generate the CSV files such that they could be printed from the camera.

## Compatibility

This has only been tested with the Instax SQ 10 camera

## Installation

```
conda create -n instax python=3.8
conda activate instax
poetry install
```

## Usage

See usage via the CLI help message

```
instax-convert --help
```
