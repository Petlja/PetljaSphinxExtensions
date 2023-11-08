if( 'undefined' === typeof window){
    importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js");
} 

var pyodide = null;
var id = null;

const reactPyModule = {
    getInput: (id, prompt) => {
        const request = new XMLHttpRequest()
        request.open('GET', `/py-get-input/?id=${id}&prompt=${prompt}`, false)
        request.send(null)
        return request.responseText
    }
}

function postToMainThread(message){
    message.id = id;
    self.postMessage(message);
}

self.onmessage = async function (event) {
    if(event.data.type === "ID"){
        id = event.data.id;
        await setupPyodide();
    }
    if (event.data.type === "INSTALL") {
        id = event.data.id;
        await install_package(event.data.packages);
        postToMainThread({ type: "PACKAGES_INSTALLED" });
    }

    if (event.data.type === "RUN") {
        try{
            pyodide.runPython(`run_code('''${event.data.code}''')`)
        }catch(e){
            postToMainThread({ type: "STDERR", text: e.toString() })
        }
    }
}

async function install_package(packages) {
    micropip = pyodide.pyimport('micropip')
    packages.forEach(async (p) => {
        await micropip.install(p)
    });
}

async function setupPyodide() {
    pyodide = await self.loadPyodide({
        stdout: (text) => {
            postToMainThread({ type: "STDOUT", text: text })
        },
        stderr: (text) => {
            postToMainThread({ type: "STDERR", text: text })
        }
    });
    await pyodide.loadPackage(['pyodide-http'])
    await pyodide.loadPackage(['micropip'])
    pyodide.registerJsModule('react_py', reactPyModule)

    const initCode = `
import pyodide_http
pyodide_http.patch_all()
`
    await pyodide.runPythonAsync(initCode)
    
    const patchInputCode = `
import sys, builtins
import react_py
__prompt_str__ = ""
def get_input(prompt=""):
    global __prompt_str__
    __prompt_str__ = prompt
    print(prompt)
    s = react_py.getInput("${id}", prompt)
    print(s)
    return s
builtins.input = get_input
sys.stdin.readline = lambda: react_py.getInput("${id}", __prompt_str__)
`
    await pyodide.runPythonAsync(patchInputCode)

    const patchOutputCode = `
import sys, io, traceback
def run_code(code):
    try:
        exec(code, {})
    except:
        traceback.print_exc()
`
    await pyodide.runPythonAsync(patchOutputCode);
    
    postToMainThread({ type: "PYODIDE_READY" });
}




