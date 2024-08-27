# ARTIQ NDSP for Andro iXon Ultra 897 camera

## Features

- *Image* mode readout
- sub-area selection
- pixel binning (superpixel mode)
- trigger source setting
- exposure time setting
- sensor noise measurement (shutter closed acqisition)
- software or external trigger 
- cooler control
- gain control


## Implementation notes

### Image readout

> To prevent smearing the image, light must be prevented from falling onto the CCD during the readout process.

### Superpixels

- better SNR
- increased speed

### Why not cropped mode?

> NOTE: It is important to ensure that no light falls on the excluded region otherwise the acquired data will be corrupted.

### Setting sub-area

```
# Full resolution image
SetReadMode(4);
SetImage(1,1,1,1024,1,256);
```

### Acquisition modes

- basic operation will be *Single Scan*, just setting exposure time (`SetExposureTime(s)`)
- acquistion must be started via `StartAcquisition` function

### Shutter

- fully auto or permanently open
- option to set temporarily *permanently closed* to make background scan


### Real exposure time

> Due to the time needed to shift charge into the shift register, digitize it and operate shutters, where necessary, the exposure time cannot be set to just any value. For example, the minimum exposure time depends on many factors including the readout mode, trigger mode and the digitizing rate. To help the user determine what the actual exposure time will be the driver automatically calculates the nearest allowed value, not less than the user’s choice. The actual calculated exposure time used by Andor SDK may be obtained via the GetAcquisitionTimings function (this function should be called after the acquisition details have been fully defined i.e. readout mode, trigger mode etc. have been set).

### Kitetic Series

> NOTE: In External Trigger mode the delay between each scan making up the acquisition is not under the control of the Andor SDK, but is synchronized to an externally generated trigger pulse.

- this may be useful for obtaining to circular software buffer several images and downloading them after the experiment

### To be determined

- minimum time between acquisitions (minimum Kitetic Time?)

### Distribution

- preferred way is Docker container
- packages:
    - NDSP (this repo) - will require pyAndorSDK2 installation as requirement
    - container - in MIKOK_LLI?
- looks like Andor SDK does not require custom kernel modules
- we only need to make sure created devices are writable for container user