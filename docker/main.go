package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"syscall"
)

// docker 		  run image <cmd> <params>
// go run main.go run 	    <cmd> <params>

func main() {
	switch os.Args[1] {
	// Parent process
	case "run":
		run()
	// Child process
	case "child":
		child()
	default:
		panic("bad command")
	}
}

func run() {
	fmt.Printf("Running %v as %d\n", os.Args[2:], os.Getpid())

	cmd := exec.Command("/proc/self/exe", append([]string{"child"}, os.Args[2:]...)...)
	// Connect child input to this terminal
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	//Give child a new hostname namespace
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Cloneflags: syscall.CLONE_NEWUTS | syscall.CLONE_NEWPID | syscall.CLONE_NEWNS,
		Unshareflags: syscall.CLONE_NEWNS
	}
	cmd.Run()
}

func child() {
	fmt.Printf("Running %v\n", os.Args[2:])

	// Set the child namespace hostname
	syscall.Sethostname([]bytes("container"))
	syscall.Chroot("/vagrant/ubuntu-fs")
	syscall.Chdir("/")
	syscall.Mount("proc", "proc", "proc", 0, "")

	cmd := exec.Command(os.Args[2], os.Args[3:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Cloneflags: syscall.CLONE_NEWUTS,
	}

	cmd.Run()

	syscall.Unmount("/proc", 0)
}

func cg() {
	cgroups := "/sys/fs/cgroup/"
	pids := filepath.Join(cgroups, "pids")
	err := os.Mkdir(filepath.Join(pids, "liz"), 0755)
	if err != nil && !os.IsExist(err) {
		panic(err)
	}
	// Only 20 processes
	must(ioutil.WriteFile(filepath.Join(pids, "liz/pids.max"), []byte("20"), 0700))
	// Remove the new cgroup in place after the container exits 
	must(ioutil.WriteFile(filepath.Join(pids, "liz/notify_on_release"), []byte("1"), 0700))
	must(ioutil.WriteFile(filepath.Join(pids, "liz/cgroups.procs"), []byte(strconv.Itoa(os.Getpid())), 0700))
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
