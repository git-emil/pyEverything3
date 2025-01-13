'''
The `Everything3` class is a Python wrapper for the Everything SDK3 library,
which provides a powerful file search functionality. The class handles the
initialization and setup of the SDK, including loading the necessary DLL,
creating and managing the search state, and connecting to the Everything client.

The `search` method is the main entry point for performing file searches.
It takes a search pattern and returns a list of full paths for the matching 
files and folders. The method sets the search parameters, executes the search, 
and retrieves the results, handling the necessary SDK calls and cleanup.

The search pattern support numerous search modifiers and options.
Read this page: https://www.voidtools.com/support/everything/searching/

Finally, the `__del__` method is responsible for cleaning up the resources
used by the class, such as the search state and the client connection,
when the object is destroyed.

2025-01-09, Emil

'''
import ctypes
import os
from typing import List, Tuple
from glob import glob
import time
#from everything3_constants import EVT3

# default location of the dll
FQP_EVT = "C:/Program Files/Everything/Everything3_x64.dll"
if not os.path.exists(FQP_EVT):
    # search for dll at most likely locations
    search_paths = [
        "C:/Program Files*/*/Everything3_x64.dll",
        f"{Path.home()}/AppData/*/*/Everything3_x64.dll"
    ]
    for pattern in search_paths:
        matches = glob(pattern, recursive=True)
        if matches:
            FQP_EVT = matches[0]
            break

class Everything3:
    """Everything SDK v3 Python wrapper"""

    def __init__(self):
        if not os.path.exists(FQP_EVT):
            raise FileNotFoundError("Everything3_x64.dll not found")

        self.dll = ctypes.WinDLL(FQP_EVT)
        self.max_path = 1024
        self._setup_functions()

        self.client = self.dll.Everything3_ConnectW("1.5a")
        if not self.client:
            self.client = self.dll.Everything3_ConnectW(None)
            if not self.client:
                raise RuntimeError("Failed to connect to Everything service")

        self.search_state = self.dll.Everything3_CreateSearchState()
        if not self.search_state:
            raise RuntimeError("Failed to create search state")

    def __del__(self):
        if hasattr(self, 'search_state'):
            self.dll.Everything3_DestroySearchState(self.search_state)
        if hasattr(self, 'client'):
            self.dll.Everything3_DestroyClient(self.client)

    def _setup_functions(self):
        """Setup function prototypes for SDK3"""
        self.dll.Everything3_CreateSearchState.argtypes = []
        self.dll.Everything3_CreateSearchState.restype = ctypes.c_void_p

        self.dll.Everything3_DestroySearchState.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_DestroySearchState.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Everything3_SetSearchTextW.restype = ctypes.c_bool

        self.dll.Everything3_ConnectW.argtypes = [ctypes.c_wchar_p]
        self.dll.Everything3_ConnectW.restype = ctypes.c_void_p

        self.dll.Everything3_DestroyClient.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_DestroyClient.restype = ctypes.c_bool

        self.dll.Everything3_Search.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.dll.Everything3_Search.restype = ctypes.c_void_p

        self.dll.Everything3_GetResultListCount.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_GetResultListCount.restype = ctypes.c_size_t

        self.dll.Everything3_GetResultFullPathNameW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_wchar_p,
            ctypes.c_size_t
        ]
        self.dll.Everything3_GetResultFullPathNameW.restype = ctypes.c_size_t

        # Add to existing function setups:
        self.dll.Everything3_GetResultPropertyBlob.argtypes = [
            ctypes.c_void_p,      # result_list
            ctypes.c_size_t,      # result_index
            ctypes.c_ulong,       # property_id
            ctypes.POINTER(ctypes.c_byte),  # buf
            ctypes.POINTER(ctypes.c_size_t) # pbufsize
        ]
        self.dll.Everything3_GetResultPropertyBlob.restype = ctypes.c_bool

        self.dll.Everything3_DestroyResultList.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_DestroyResultList.restype = ctypes.c_bool

    def search(self, pattern: str) -> List[str]:
        """
        Perform a search and return list of full paths

        Args:
            pattern: Search pattern
            offset: Start index for results
            count: Maximum number of results (0 for unlimited)

        Returns:
            The number of matching items

        Fills "items" with the paths of all fond items
        """
        self.dll.Everything3_SetSearchTextW(self.search_state, pattern)
        result_list = self.dll.Everything3_Search(self.client, self.search_state)
        if not result_list:
            return []
        num_results = self.dll.Everything3_GetResultListCount(result_list)
        _path_buffer = ctypes.create_unicode_buffer(self.max_path)
        self.items = [self.dll.Everything3_GetResultFullPathNameW(result_list, i, _path_buffer, self.max_path) or _path_buffer.value
                for i in range(num_results)]
        self.dll.Everything3_DestroyResultList(result_list)
        return len(self.items)

    def count(self, pattern: str) -> List[str]:
        """
        Perform a search and return list of full paths

        Args:
            pattern: Search pattern
            offset: Start index for results
            count: Maximum number of results (0 for unlimited)

        Returns:
            The number of matching items
        """
        self.dll.Everything3_SetSearchTextW(self.search_state, pattern)
        result_list = self.dll.Everything3_Search(self.client, self.search_state)
        if not result_list:
            return 0
        return self.dll.Everything3_GetResultListCount(result_list)

if __name__ == "__main__":
    EVT = Everything3()

    phrases = ["* ext:txt", "* ext:cfg", "* ext:ini", "files:", "folders:", "*"]

    for phrase in phrases:
        start = time.perf_counter()
        amount = EVT.count(phrase)
        elapsed = time.perf_counter() - start
        print(f'Phrase "{phrase:12}" - Time: {elapsed:.4f}s, Results: {amount}')

    pass
