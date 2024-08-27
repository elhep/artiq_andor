import argparse

from sipyco.pc_rpc import simple_server_loop
from sipyco import common_args
from andor.driver import AndorCamera


def get_argparser():
    parser = argparse.ArgumentParser(
        description="ARTIQ controller for the Lab Brick Digital Attenuator")
    common_args.simple_network_args(parser, 3253)
    common_args.verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    common_args.init_logger_from_args(args)
    andor = AndorCamera()
    try:
        andor.enable_cooling()
        andor.enable_cameralink()
        
        simple_server_loop({"camera": andor},
                           common_args.bind_address_from_args(args), args.port)
    finally:
        andor.close()

if __name__ == "__main__":
    main()