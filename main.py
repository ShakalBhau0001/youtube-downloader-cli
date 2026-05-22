import sys
from cli.commands import build_parser, run_args
from cli.interactive import run_interactive


def main():
    if len(sys.argv) == 1:
        try:
            run_interactive()
        except KeyboardInterrupt:
            print("\n\nCancelled.")
        return

    parser = build_parser()
    args = parser.parse_args()

    if not args.url:
        try:
            run_interactive()
        except KeyboardInterrupt:
            print("\n\nCancelled.")
        return

    try:
        run_args(args)
    except KeyboardInterrupt:
        print("\n\nCancelled.")


if __name__ == "__main__":
    main()
