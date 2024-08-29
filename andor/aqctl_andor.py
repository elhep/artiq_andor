import argparse

from sipyco.pc_rpc import simple_server_loop
from sipyco import common_args
from andor.driver import AndorCamera, logger


def get_argparser():
    parser = argparse.ArgumentParser(
        description="ARTIQ controller for the Andor iXon Ultra 897 camera.")
    common_args.simple_network_args(parser, 3253)
    common_args.verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    common_args.init_logger_from_args(args)
    logger.info(f"Starting NDSP controller...")
    andor = AndorCamera()
    try:
        andor.init()        
        simple_server_loop({"camera": andor},
                           common_args.bind_address_from_args(args), args.port)
    finally:
        andor.close()

if __name__ == "__main__":
    main()