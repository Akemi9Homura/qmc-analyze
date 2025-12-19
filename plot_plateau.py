import re
import argparse
import numpy as np
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(
        description="Plot FCIQMC1 warm-up walker numbers (log y by default)."
    )
    parser.add_argument("file", help="Path to log file")
    parser.add_argument("--end", type=int, default=None, help="Only plot steps <= end")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
        s = f.read()

    # only fciqmc1 section
    i0 = s.find("warm up for fciqmc1")
    i1 = s.find("warm up for fciqmc2", i0)
    if i0 < 0:
        raise SystemExit("Cannot find 'warm up for fciqmc1' in log.")
    if i1 < 0:
        i1 = len(s)
    s = s[i0:i1]

    # extract (step, walker)
    pattern = re.compile(
        r"step:\s*(\d+),\s*walker number:\s*([+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)"
    )
    pairs = pattern.findall(s)
    if not pairs:
        raise SystemExit(
            "No 'step: ..., walker number: ...' lines found in fciqmc1 section."
        )

    steps = np.fromiter((int(a) for a, _ in pairs), dtype=np.int64)
    walkers = np.fromiter((float(b) for _, b in pairs), dtype=np.float64)

    # optional truncate
    if args.end is not None:
        mask = steps <= args.end
        steps, walkers = steps[mask], walkers[mask]

    # log-y requires walkers > 0
    mask = walkers > 0
    steps, walkers = steps[mask], walkers[mask]

    plt.plot(steps, walkers)
    plt.yscale("log")  # 默认对数纵坐标
    plt.xlabel("step")
    plt.ylabel("walker number")
    plt.title("FCIQMC1 warm up (log y)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
