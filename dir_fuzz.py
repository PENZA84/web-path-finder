import argparse
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

parser=argparse.ArgumentParser()

parser.add_argument("url", help="Follow by url to recon")
parser.add_argument("-w", "--wordlist", help="Followed by wordlist file path.", required=True)
parser.add_argument("-th", "--threads", help="Concurrent threads (1-1000). Default: 40", type=int, default=40)
parser.add_argument("-t", "--timeout", help="Followed by timeout desired in seconds. By default it'll be 10 seconds", type=int, default=10)
parser.add_argument("-o", "--output", help="File to save the results", default=None)

args=parser.parse_args()



def path_fuzzer(url, timeout, path):
    final_url=urljoin(url.rstrip('/')+'/', path.lstrip('/'))                    #Target url construction
    req=urllib.request.Request(final_url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}, method="GET")

    try:
        response=urllib.request.urlopen(req, timeout=timeout)

        size_str=None
        size_bytes=response.headers.get("Content-Length")
        if size_bytes is not None:
            try:
                size_bytes = int(size_bytes)
                if size_bytes>1024*1024*1024:
                    size_str=f"(size: {size_bytes/(1024*1024*1024):.2f}GB)"
                elif size_bytes>1024*1024:
                    size_str=f"(size: {size_bytes/(1024*1024):.2f}MB)"
                elif size_bytes>1024:
                    size_str=f"(size: {size_bytes/(1024):.2f}KB)"
                else:
                    size_str=f"(size: {size_bytes:.2f}B)"
            except (TypeError, ValueError):
                size_str = None

        
        sensitive_keywords = [".git", ".env", "config", "configuration", "settings", "backup", "backups", "dump", "database", "db", "wp-config", "wordpress", "joomla", "admin", "api", "dashboard", "panel", "logs", "log"]
        sensitive=None
        path_lower=path.lower()
        if any(keyword in path_lower for keyword in sensitive_keywords):
            sensitive="(sensitive file exposed)"
                
                

        return path, response.code, response.reason, size_str, sensitive

    except urllib.error.HTTPError as e:
        return path, e.code, e.reason, None, None

    except urllib.error.URLError as e:
        return path, None, e.reason, None, None

    except Exception as e:
        return path, None, str(e), None, None

    




if args.url and args.wordlist:
    interrupted=False
    start_time=time.time()
    #Validate url's protocol
    if not args.url.startswith(('http://', 'https://')):
        base_url=args.url

        detected=None

        for proto in ["https://", "http://"]:
            test_url=proto+base_url

            try:
                req=urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}, method="GET")
                urllib.request.urlopen(req, timeout=args.timeout)

                detected = test_url
                break
            except Exception:
                continue

        if detected:
            args.url=detected
            print(f"[!] Auto-detected working protocol: {args.url}\n")
        else:
            print("[!] Could not detect protocol. Defaulting to HTTP\n")
            args.url = "http://" + base_url

    url=args.url


    with open(f"{args.wordlist}", "r", encoding="utf-8", errors="ignore") as f:                                                        #Read wordlist
        paths = [line.strip() for line in f if line.strip()]                                        #Filter empty lines


    out_file = open(args.output, "w") if args.output else None                                      #Open output file in writing mode


    workers=max(1, min(1000, args.threads))
    executor=ThreadPoolExecutor(max_workers=workers)
    try:
        print(f"[+] Testing paths against {args.url}...")

        if out_file:
            out_file.write(f"[+] Testing paths against {args.url}...\n")

        #Threading with ThreadPoolExecutor

        futures=[executor.submit(path_fuzzer, args.url, args.timeout, path) for path in paths]

        for future in as_completed(futures):
            temp=future.result()

            if temp[1] is not None and temp[1] not in [404, 429]:                                              #404: Doesn't Exist, 429: Rate Limit
                #Formatting summary
                line = f"{'':>{20}}/{temp[0]:<40} {temp[1]:>5} {temp[2]:<20}"
                if temp[3]:
                    line+=f"{temp[3]:<20}"
                if temp[4]:
                    line+=f"{temp[4]}"
                
                print(line)

                if out_file:
                    out_file.write(line + "\n")

    except KeyboardInterrupt:
        elapsed_time=time.time()-start_time
        print(f"\n[INFO] Scan interrupted by user. Scan executed during {elapsed_time:.2f} seconds.\nShutting down...")
        interrupted=True
    
    finally:
        executor.shutdown(wait=False)
        if out_file:
            out_file.close()
            print(f"\n[+] Results saved to {args.output}")

        if not interrupted:
            elapsed_time=time.time()-start_time
            print(f"\n[INFO] Scan completed in {elapsed_time:.2f} seconds\n")


