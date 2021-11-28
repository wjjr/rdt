from rdt import *


def str2int(str_n: [str, bytes]) -> int:
    try:
        return int(str_n)
    except:
        return -1


def run_server(address, simulate_unreliability, num_packets):
    rdt_init(address, bind=True, simulate_unreliability=simulate_unreliability)

    max_n = num_packets
    next_n = 0

    arrived = set()
    safe = set()
    delayed = set()
    missing = set()
    corrupt = set()
    duplicated = []

    try:
        while next_n < max_n:
            data, _ = rdt_recv()

            i1 = str2int(data[0:6])
            pad1 = data[6:13]
            i2 = str2int(data[13:19])
            pad2 = data[19:26]
            i3 = str2int(data[26:32])

            is_corrupt = not (i1 == i2 == i3 and pad1 == pad2 == (b'\xff' * 7))
            n = i1 if i1 == i2 else i3

            if is_corrupt:
                corrupt.add(n)

            if n in arrived:
                duplicated.append(n)
                print(f"{n:06d} is a clone!" +
                      (", and it's broken :p" if is_corrupt else ''))
            elif n in missing:
                delayed.add(n)
                missing.remove(n)
                print(f"{n:06d} finally arrived!" +
                      (', but broken ;(' if is_corrupt else ''))
            else:
                if n > next_n:
                    for i in range(next_n, n):
                        missing.add(i)
                        print(f"Where's {i:06d}?")

                if not is_corrupt:
                    safe.add(n)
                    print(f"{n:06d} arrived =)")
                else:
                    print(f"{n:06d} arrived broken ;(")

                next_n = n + 1

            arrived.add(n)
    except KeyboardInterrupt:
        print("Ok, I'm going to rest...")

    total = len(arrived) + len(duplicated)
    safe_len = len(safe)
    delayed_len = len(delayed)
    lost_len = len(missing)
    corrupt_len = len(corrupt)
    duplicated_len = len(duplicated)
    p = max_n / 100

    print('\nServer stats:')
    print(f"* Received {total} ({total / p:.3f}%) of the {max_n} expected packets:")
    print(f"  {safe_len:6d} ({safe_len / p:7.3f}%) safe packets")
    print(f"  {delayed_len:6d} ({delayed_len / p:7.3f}%) delayed packets")
    print(f"  {lost_len:6d} ({lost_len / p:7.3f}%) lost packets")
    print(f"  {corrupt_len:6d} ({corrupt_len / p:7.3f}%) corrupt packets")
    print(f"  {duplicated_len:6d} ({duplicated_len / p:7.3f}%) duplicated packets")

    rdt_stats(pprint=True)
