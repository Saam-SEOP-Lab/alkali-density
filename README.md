# Alkali Metal Density Measurement

A tool for data collection and analysis of faraday rotation in alkali metal vapor. 

## Description

Calculations of alkali metal density are based on 
$$
\theta_B = [A]B\frac{e^2l\mu_B}{6mhc}\left(\frac{\lambda^2}{3c^2}\left(\frac{4\lambda_1^2}{(\lambda_1-\lambda)^2}+\frac{7\lambda_2^2}{(\lambda_2-\lambda)^2}-\frac{2\lambda_1\lambda_2}{(\lambda_1-\lambda)(\lambda_2-\lambda)}\right)-\frac{\lambda h}{kT}\left(\frac{\lambda_1}{(\lambda_1-\lambda)} - \frac{\lambda_2}{(\lambda_2-\lambda)}\right)\right)
$$

## Getting Started
To get set up to develop this project you will need macOS Sonoma or Windows 10/11. You likely can also run this on several varieties of linux, but I have not specifically tried to set that up and can offer no additional guidance beyond what is needed for the mac set up. 

You will also need Python 3.12 or later installed. You may be able to get this working on an older version of Python, but I do not make any promises. You are entering unknown territory and any monsters you encounter are entirely not my fault.

You will also need at least one free USB port. 

### Package Manager

You will likely want some sort of package manager to manage all the external python libraries. I have been using Anaconda with reasonable success. However, I am not the boss of you. Choose your favorite package manager or download everything the old fashioned way, if you would like to live confusingly. 

### Required Libraries

The following libraries are used by the alkali metal density program:
* Numpy
* Matplotlib
* Pymeasure
* Pyvisa
* Pandas
* PyQt5
* Tkinter(?)

### Equipment

To actually make the measurements you will need an oscilloscope capable of connecting to a computer via a usb cable (this will likely be a USB-A to USB-B sorry). I used a tektronics educational series scope, but this should work with any scope that NI VISA can recognize. Though you may need to change the name of the scope in the code. 

### External Software

Which brings me to other support software you will need. You will want to install National Instrument's Interactive Visa manager so that you can easily determine whether your computer is actually recognizing the instruments you have plugged into it. You may also need to install other NI drivers depending on your operating system (Windows f*cking loves making you install a series of drivers). NI package manager will also be helpful in maintaining all the national instruments stuff on a windows operating system. 

### Executing program from the IDE

To run the program from the IDE, run the file located at \density_app\app.py

## Authors

E. Terry-Welsh (eleanor.terry-welsh@wsu.edu)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)