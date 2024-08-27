import logging
from pyAndorSDK2 import atmcd, atmcd_codes, atmcd_errors
import time
import numpy as np


logger = logging.getLogger("andor")


def check(ret, call):
    if ret != atmcd_errors.Error_Codes.DRV_SUCCESS:
        logger.error(f"{call}: error code {ret}")
        raise RuntimeError(f"{call}: error code {ret}")


class AndorCamera:

    def __init__(self):
        self.sdk = atmcd()
        
        ret = self.sdk.Initialize("")
        check(ret, "Initialize")

        (ret, iSerialNumber) = self.sdk.GetCameraSerialNumber()
        check(ret, "GetCameraSerialNumber")
        logger.info(f"Camera serial number: {iSerialNumber}")

        self.acquisition_ready = False
        self.x_pixels = 0
        self.y_pixels = 0

    def close(self):
        logger.info("Closing camera")

        # Close shutter
        ret = self.sdk.SetShutter(0, atmcd_codes.Shutter_Mode.PERMANENTLY_CLOSED, 0, 0)
        check(ret, "SetShutter")
        logger.info("Shutter closed")

        # Turn off cooler
        ret = self.sdk.CoolerOFF()
        check(ret, "CoolerOFF")
        logger.info("Cooler turned off")

        # Shut down SDK
        ret = self.sdk.ShutDown()
        check(ret, "ShutDown")
        logger.info("SDK shut down")

    def enable_cooling(self, target_temperature=-60):
        ret = self.sdk.SetTemperature(target_temperature)
        check(ret, "SetTemperature")

        ret = self.sdk.CoolerON()
        check(ret, "CoolerON")
    
    def ensure_temperature_stabilized(self):
        while True:
            (ret, temperature) = self.sdk.GetTemperature()
            logger.info(f"Current temperature: {temperature}")
            if ret == atmcd_errors.Error_Codes.DRV_TEMP_STABILIZED:
                break
            else:
                time.sleep(5)
        logger.info("Temperature stabilized")

    def enable_cameralink(self):
        ret = self.sdk.SetCameraLinkMode(1)
        check(ret, "SetCameraLinkMode -> 1")

    def disable_cameralink(self):
        ret = self.sdk.SetCameraLinkMode(0)
        check(ret, "SetCameraLinkMode -> 0")

    def configure_acquisition(self, trigger="internal", exposure_time=0.01, shutter_open=True, em_gain=100, image_config=None):
        assert trigger in ["internal", "external"]

        ret = self.sdk.SetAcquisitionMode(atmcd_codes.Acquisition_Mode.SINGLE_SCAN)
        check(ret, "SetAcquisitionMode")

        ret = self.sdk.SetReadMode(atmcd_codes.Read_Mode.IMAGE)
        check(ret, "SetReadMode")

        if shutter_open:
            shutter_mode = atmcd_codes.Shutter_Mode.PERMANENTLY_OPEN
        else:
            shutter_mode = atmcd_codes.Shutter_Mode.PERMANENTLY_CLOSED
        ret = self.sdk.SetShutter(0, shutter_mode, 0, 0)
        check(ret, "SetShutter")

        ret = self.sdk.SetExposureTime(exposure_time)
        check(ret, "SetExposureTime")

        (ret, fminExposure, fAccumulate, fKinetic) = self.sdk.GetAcquisitionTimings()
        check(ret, "GetAcquisitionTimings")
        logger.info(f"Reported acquisition times: exposure {fminExposure}, accumulate: {fAccumulate}, kinetic: {fKinetic}")
    
        # Set Real EM gain mode
        ret = self.sdk.SetEMGainMode(3)
        check(ret, "SetEMGainMode")

        # FIXME: This way of setting EM gain is not working
        # ret = self.sdk.SetGain(em_gain)
        # check(ret, "SetGain")

        if image_config is None:
            (ret, xpixels, ypixels) = self.sdk.GetDetector()
            check(ret, "GetDetector")
            image_config = {
                "hbin": 1,
                "vbin": 1,
                "hstart": 1,
                "hend": xpixels,
                "vstart": 1,
                "vend": ypixels,
            }
        # TODO: How binning affects image size for values not being powers of 2?
        assert image_config["hbin"] == image_config["vbin"] == 1, "Superpixels are not supported yet"
        self.x_pixels = image_config["hend"] - image_config["hstart"] + 1
        self.y_pixels = image_config["vend"] - image_config["vstart"] + 1

        ret = self.sdk.SetImage(**image_config)
        check(ret, "SetImage")
        logger.info(f"Image configuration: hbin {image_config['hbin']}, vbin {image_config['vbin']}, hstart {image_config['hstart']}, hend {image_config['hend']}, vstart {image_config['vstart']}, vend {image_config['vend']}")
        
        if trigger == "internal":
            trigger_mode = atmcd_codes.Trigger_Mode.INTERNAL
        elif trigger == "external":
            trigger_mode = atmcd_codes.Trigger_Mode.EXTERNAL
        ret = self.sdk.SetTriggerMode(trigger_mode)
        check(ret, "SetTriggerMode")

        ret = self.sdk.PrepareAcquisition()
        print("Function PrepareAcquisition returned {}".format(ret))

        self.acquisition_ready = True

    def start_acquisition(self):
        assert self.acquisition_ready, "Acquisition not ready"

        ret = self.sdk.StartAcquisition()
        check(ret, "StartAcquisition")

    def get_image(self):
        # TODO: Add support for SDK-backed multiple acquisitions
        ret = self.sdk.WaitForAcquisition()
        print("Function WaitForAcquisition returned {}".format(ret))

        (ret, arr) = self.sdk.GetMostRecentImage16(self.x_pixels * self.y_pixels)
        check(ret, "GetMostRecentImage16")

        return np.reshape(arr, (self.x_pixels, self.y_pixels))
