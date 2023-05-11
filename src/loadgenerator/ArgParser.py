import argparse

class StringProcessor:
    def __init__(self):
        self.pattern = None
    
    def parse_args(self):
        # Parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--pattern", type=str, required=True,
                            help="The pattern: e.g. bursty or mild")
        try:
            args = parser.parse_args()
            self.pattern = args.pattern
        except Exception as e:
            print(f"Unexpected error occurred: {e}\nCheck arguments.")

        return self.pattern