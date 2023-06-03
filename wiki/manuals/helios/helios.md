# HELIOS

<https://heliosexo.readthedocs.io/>

Seems to work only on GNU/Linux and with NVIDIA GPU / video card. At least, the author claims that there is no support for Windows, though it might just as well work, since the HELIOS itself is Python.

<!-- MarkdownTOC -->

- [Installation](#installation)
    - [NVIDIA CUDA Toolkit](#nvidia-cuda-toolkit)
        - [On WSL](#on-wsl)
    - [The package](#the-package)
- [How to use it](#how-to-use-it)
    - [Generating chemical abundances](#generating-chemical-abundances)
        - [FastChem](#fastchem)
            - [Building](#building)
            - [Generating output](#generating-output)

<!-- /MarkdownTOC -->

## Installation

### NVIDIA CUDA Toolkit

#### On WSL

<https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_local>

``` sh
$ wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
$ sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
$ wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-wsl-ubuntu-12-1-local_12.1.0-1_amd64.deb
$ sudo dpkg -i cuda-repo-wsl-ubuntu-12-1-local_12.1.0-1_amd64.deb
$ sudo cp /var/cuda-repo-wsl-ubuntu-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/
$ sudo apt update
$ sudo apt install cuda
$ sudo apt install nvidia-cuda-toolkit
```

``` sh
$ nano ~/.bash_profile

# CUDA
export PATH=/usr/local/cuda/bin:$PATH
export DYLD_LIBRARY_PATH=/usr/local/cuda/lib:$DYLD_LIBRARY_PATH

$ source ~/.bash_profile
```

``` sh
$ cd ~/code
$ git clone https://github.com/nvidia/cuda-samples
$ cd ./cuda-samples/Samples/1_Utilities/deviceQuery
$ make

$ ./deviceQuery
./deviceQuery Starting...

 CUDA Device Query (Runtime API) version (CUDART static linking)

Detected 1 CUDA Capable device(s)

Device 0: "NVIDIA GeForce GTX 1660 SUPER"
  CUDA Driver Version / Runtime Version          12.0 / 12.1
  CUDA Capability Major/Minor version number:    7.5
  Total amount of global memory:                 6144 MBytes (6441992192 bytes)
  (022) Multiprocessors, (064) CUDA Cores/MP:    1408 CUDA Cores
  GPU Max Clock rate:                            1830 MHz (1.83 GHz)
  Memory Clock rate:                             7001 Mhz
  Memory Bus Width:                              192-bit
  L2 Cache Size:                                 1572864 bytes
  Maximum Texture Dimension Size (x,y,z)         1D=(131072), 2D=(131072, 65536), 3D=(16384, 16384, 16384)
  Maximum Layered 1D Texture Size, (num) layers  1D=(32768), 2048 layers
  Maximum Layered 2D Texture Size, (num) layers  2D=(32768, 32768), 2048 layers
  Total amount of constant memory:               65536 bytes
  Total amount of shared memory per block:       49152 bytes
  Total shared memory per multiprocessor:        65536 bytes
  Total number of registers available per block: 65536
  Warp size:                                     32
  Maximum number of threads per multiprocessor:  1024
  Maximum number of threads per block:           1024
  Max dimension size of a thread block (x,y,z): (1024, 1024, 64)
  Max dimension size of a grid size    (x,y,z): (2147483647, 65535, 65535)
  Maximum memory pitch:                          2147483647 bytes
  Texture alignment:                             512 bytes
  Concurrent copy and kernel execution:          Yes with 2 copy engine(s)
  Run time limit on kernels:                     Yes
  Integrated GPU sharing Host Memory:            No
  Support host page-locked memory mapping:       Yes
  Alignment requirement for Surfaces:            Yes
  Device has ECC support:                        Disabled
  Device supports Unified Addressing (UVA):      Yes
  Device supports Managed Memory:                Yes
  Device supports Compute Preemption:            Yes
  Supports Cooperative Kernel Launch:            Yes
  Supports MultiDevice Co-op Kernel Launch:      No
  Device PCI Domain ID / Bus ID / location ID:   0 / 1 / 0
  Compute Mode:
     < Default (multiple host threads can use ::cudaSetDevice() with device simultaneously) >

deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 12.0, CUDA Runtime Version = 12.1, NumDevs = 1
Result = PASS
```

The HELIOS package will be making plots, which expect a GUI backend for Matplotlib. This one works fine from within WSL:

``` sh
$ sudo apt install python3-tk
```

### The package

``` sh
$ pip install pycuda h5py matplotlib numpy scipy astropy numba

$ cd ~/code
$ git clone https://github.com/exoclime/HELIOS.git helios
$ cd ./helios
$ wget -r -np -nH -R "index.html*" --cut-dirs=3 -P input https://chaldene.unibe.ch/data/helios/input_files/
```

## How to use it

``` sh
$ cd /path/to/helios/
$ python ./helios.py
$ cd ./plotting/ # plotting scripts refer to ".." path
$ python ./plot_spectrum.py
$ python ./plot_tp.py
```

### Generating chemical abundances

#### FastChem

A more detailed documentation is in the [official manual](https://github.com/exoclime/FastChem/blob/master/manual/fastchem_manual.pdf).

##### Building

FastChem is a C++ library and a CLI tool, using which you can generate a new input for HELIOS. For that you first need to build it from sources. There is also an option to make a Python module out of the library (*via pybind11*), but this is not required.

Install OpenMP dependency, in case of Mac OS:

``` sh
$ brew install libomp
```

Get the sources and apply the patch (*on top of `43c07f4a0f76e1b3b325f13e497b0a9e2ebdf818` commit*) to fix some things in the project (*mostly CMake*):

``` sh
$ git clone git@github.com:exoclime/FastChem.git
$ cd ./FastChem
$ git checkout 43c07f4a0f76e1b3b325f13e497b0a9e2ebdf818
$ git apply /path/to/FastChem.patch
```

Now you can build it:

``` sh
$ mkdir build && cd $_
$ cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="../install" -DUSE_PYTHON=0 ..
$ cmake --build . --target install
```

The `build` folder is important, because that is where (*patched*) `fastchem_python_wrapper.cpp` expects to find stuff.

On Mac OS you'll also need to add these OpenMP flags for CMake project configuration:

``` sh
$ cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="../install" -DUSE_PYTHON=0 \
    -DOpenMP_CXX_FLAGS="-Xpreprocessor -fopenmp -I/usr/local/opt/libomp/include" \
    -DOpenMP_CXX_LIB_NAMES="omp" \
    -DOpenMP_omp_LIBRARY=/usr/local/opt/libomp/lib/libomp.dylib \
    ..
```

If you enabled `-DUSE_PYTHON=1` and [got this](https://github.com/sirfz/tesserocr/issues/298):

``` sh
error: member access into incomplete type 'PyFrameObject' (aka '_frame')
```

then use an older Python (*and make sure CMake discovers exactly that one*) or update pybind11 to the latest version (*change the commit hash in `FetchContent_Declare`*).

##### Generating output

Assuming that you've build and installed it as described in the [previous section](#building), so you are now inside the `build` folder:

``` sh
$ cd ../install/bin/
$ cp -r ../../input .
$ mkdir output

$ ./fastchem ./input/config.input
...

FastChem reports: convergence ok

FastChem finished!

$ ls -L1 ./output/
chemistry.dat
monitor.dat
```

To generate chemistry files for HELIOS, edit `./input/config.input` (*the one you copied to `install/bin/`*):

```
#Atmospheric profile input file
/path/to/helios/input/chemistry/fastchem_input/pt.dat

#Chemistry output file
output/chemistry.dat

#Monitor output file
output/monitor.dat

#FastChem console verbose level (1 - 4); 1 = almost silent, 4 = detailed console output
1

#Output mixing ratios (MR) or particle number densities (ND, default)
MR
```

then check `/path/to/FastChem/model_src/model_main.cpp` (*first line should be uncommented and second line should be commented*):

``` cpp
if (!(line_stream >> pressure_in >> temperature_in)) continue;
//if (!(line_stream >> temperature_in >> pressure_in)) continue;
```

then check `save_output.h` (*there should be no spaces in neither of the strings*):

``` cpp
file << std::setw(16) << std::left << "#P(bar)" << "\t"
     << std::setw(16) << std::left << "T(k)" << "\t"
     << std::setw(16) << std::left << "n_<tot>(cm-3)" << "\t"
     << std::setw(16) << std::left << "n_g(cm-3)" << "\t"
     << std::setw(16) << std::left << "m(u)";
```

and then recompile:

``` sh
$ cmake --build . --target install
```

and re-run FastChem tool (*from `install/bin/`*):

``` sh
$ rm ./output/*

$ ./fastchem ./input/config.input

$ ls -L1 ./output/
chemistry.dat
monitor.dat
```

Path to this folder now needs to be set in HELIOS'es `/path/to/HELIOS/ktable/param_ktable.dat`:

```
path to FastChem output =                       /path/to/FastChem/install/bin/output/  [directory path]                                (CL: Y)
```

And now you can run HELIOS:

``` sh
$ cd /path/to/helios/
$ python ./helios.py
```
