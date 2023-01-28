## Pol'Eirb Codes

An example of polar codes usage for secrecy. Based on [1] and built using [py_aff3ct](https://github.com/aff3ct/py_aff3ct)

___________

### Table of Contents

[Pol'Eirb Codes Overview](#overview) 

[Installation](#install)

[How to use](#usage)

___________

<a name="overview"/>

### Overview of the Project

This project's aim is to implement a form of secrecy using the polarization properties of polar codes.

It focuses on the **weak secrecy** sections in [1] and tries to implement it in a communication chain using `Aff3ct` modules.

The following Figure illustrates the problem.

![Schema of the problem](figs/schema.png)





A complete overview of the project can be found [here](report.pdf).

___________
<a name="install"/>

### Installation

**Dependencies**

[py_aff3ct](https://github.com/aff3ct/py_aff3ct)

[pyaf](https://github.com/rtajan/pyaf)




**Install the Python libraries**

First install the required Python modules.

***For Pip:***

```bash
$ pip install -r requirements.txt
```

***For Conda:***

```bash
$ conda install --file requirements.txt
```

**Setup your environment**

In order to work with different *py_aff3ct* installs, the *dotenv* library was used to track the install path of the used libraries.

First, create a *.env* file at the root of the cloned repository. Inside, write

```bash
AFF3CT_PATH=... # replace ... with the path to your folder py_aff3ct/build/lib
PYAF_PATH=...   # replace ... with the path to your folder pyaf/build/lib
THREADED_PATH=... # replace with the path to your folder pyaf/src/python
```

___________
<a name="usage"/>

### How to Use



**References**

[1] TALEB Khaled, *Physical layer security : Wiretap polar codes for secure communications*, 2022