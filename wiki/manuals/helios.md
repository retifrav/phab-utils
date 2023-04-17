# HELIOS

<https://heliosexo.readthedocs.io/>

Seems to work only on GNU/Linux and with NVIDIA GPU / video card. At least, the author claims that there is no support for Windows, though it might just as well work, since the HELIOS itself is Python.

<!-- MarkdownTOC -->

- [NVIDIA CUDA Toolkit](#nvidia-cuda-toolkit)
    - [On WSL](#on-wsl)
- [The package](#the-package)

<!-- /MarkdownTOC -->

## NVIDIA CUDA Toolkit

### On WSL

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

## The package

``` sh
$ pip install pycuda h5py matplotlib numpy scipy astropy numba

$ cd ~/code
$ git clone https://github.com/exoclime/HELIOS.git helios
$ cd ./helios
$ wget -r -np -nH -R "index.html*" --cut-dirs=3 -P input https://chaldene.unibe.ch/data/helios/input_files/

$ python ./helios.py
$ cd ./plotting/ # plotting scripts refer to ".." path
$ python ./plot_spectrum.py
$ python ./plot_tp.py
```
