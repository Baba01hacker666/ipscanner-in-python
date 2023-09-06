package main

import (
	"flag"
	"fmt"
	"os/exec"
	"sync"
)

func ping(host string, wg *sync.WaitGroup) {
	defer wg.Done()
	cmd := exec.Command("ping", "-c", "1", host)
	err := cmd.Run()
	if err == nil {
		fmt.Printf("%s is online.\n", host)
	} else {
		fmt.Printf("%s is offline.\n", host)
	}
}

func scanPort(host string, port int, wg *sync.WaitGroup) {
	defer wg.Done()
	cmd := exec.Command("nmap", "-p", fmt.Sprintf("%d", port), host)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Printf("Error scanning port %d on %s: %v\n", port, host, err)
		return
	}
	fmt.Printf("Port %d on %s is open:\n%s\n", port, host, string(output))
}

func scan(host string, np bool, ports []int, showProcess bool, wg *sync.WaitGroup) {
	defer wg.Done()
	if showProcess {
		fmt.Printf("Scanning %s...\n", host)
	}
	if !np {
		if len(ports) == 0 {
			ports = make([]int, 65535)
			for i := 1; i <= 65535; i++ {
				ports[i-1] = i
			}
		}
		var portWg sync.WaitGroup
		for _, port := range ports {
			portWg.Add(1)
			go scanPort(host, port, &portWg)
		}
		portWg.Wait()
	}
	ping(host, wg)
}

func main() {
	npFlag := flag.Bool("np", false, "Do not scan ports")
	portsFlag := flag.String("p", "", "Port number or range of ports to scan, e.g., 22 or 1-65535")
	showProcessFlag := flag.Bool("sp", false, "Show scan progress and running services")
	flag.Parse()

	args := flag.Args()
	if len(args) == 0 {
		fmt.Println("Please provide one or more IP addresses to scan.")
		return
	}

	np := *npFlag
	ports := make([]int, 0)
	showProcess := *showProcessFlag

	if *portsFlag != "" {
		// Parse the ports flag if provided
		// ...

	}

	var wg sync.WaitGroup
	for _, arg := range args {
		wg.Add(1)
		go scan(arg, np, ports, showProcess, &wg)
	}
	wg.Wait()
}