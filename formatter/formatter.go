package main

// #include <stdlib.h>
import "C"
import (
	"unsafe"

	"github.com/VictoriaMetrics/metricsql"
)

//export Format
func Format(input *C.char) *C.char {
	inputStr := C.GoString(input)
	res, err := metricsql.Prettify(inputStr)
	if err != nil {
		return nil
	}

	return C.CString(res)
}

//export FreeStr
func FreeStr(input *C.void) {
	C.free(unsafe.Pointer(input))
}

func main() {}
