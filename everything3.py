'''
The `Everything3` class is a Python wrapper for the Everything SDK3 library,
which provides a powerful file search functionality. The class handles the
initialization and setup of the SDK, including loading the necessary DLL,
creating and managing the search state, and connecting to the Everything client.

The `search` method is the main entry point for performing file searches.
It takes a search pattern, an optional offset, and an optional count, and
returns a list of full paths for the matching files and folders. The method
sets the search parameters, executes the search, and retrieves the results,
handling the necessary SDK calls and cleanup.

The class also provides a set of methods for configuring various search
options, such as case sensitivity, whole word matching, regex mode, diacritics
matching, and more. These methods allow the user to fine-tune the search
behavior to their specific needs.

Finally, the `__del__` method is responsible for cleaning up the resources
used by the class, such as the search state and the client connection,
when the object is destroyed.

2025-01-09, Emil

'''

import ctypes
import os
from ctypes import wintypes
from typing import List, Optional, Union, Tuple
# from everything3_constants import EVT3

class Everything3:
    """Everything SDK3 Python wrapper"""

    def __init__(self):
        fqp_EVT = r"C:\Program Files\Everything\Everything3_x64.dll"
        # Load DLL based on architecture
        if os.path.exists(fqp_EVT):
            self.dll = ctypes.WinDLL(fqp_EVT)
        else:
            raise FileNotFoundError("Everything3_x64.dll not found")

        self.max_path = 32767

        self._setup_functions()

        # Create and initialize search state
        self.search_state = self.dll.Everything3_CreateSearchState()
        if not self.search_state:
            raise RuntimeError("Failed to create search state")

    def _setup_functions(self):
        """Setup function prototypes for SDK3"""

         # Search state functions
        self.dll.Everything3_CreateSearchState.argtypes = []
        self.dll.Everything3_CreateSearchState.restype = ctypes.c_void_p

        self.dll.Everything3_DestroySearchState.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_DestroySearchState.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Everything3_SetSearchTextW.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchMatchPath.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchMatchPath.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchMatchCase.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchMatchCase.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchMatchWholeWords.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchMatchWholeWords.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchRegex.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchRegex.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchViewportCount.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self.dll.Everything3_SetSearchViewportCount.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchViewportOffset.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self.dll.Everything3_SetSearchViewportOffset.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchMatchDiacritics.argtypes = [ctypes.c_void_p, ctypes.c_bool]

        self.dll.Everything3_SetSearchMatchDiacritics.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchMatchPrefix.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchMatchPrefix.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchMatchSuffix.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchMatchSuffix.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchIgnorePunctuation.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchIgnorePunctuation.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchWhitespace.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchWhitespace.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchFoldersFirst.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.dll.Everything3_SetSearchFoldersFirst.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchRequestTotalSize.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchRequestTotalSize.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchHideResultOmissions.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchHideResultOmissions.restype = ctypes.c_bool

        self.dll.Everything3_SetSearchSortMix.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        self.dll.Everything3_SetSearchSortMix.restype = ctypes.c_bool

        # Client functions
        self.dll.Everything3_ConnectW.argtypes = [ctypes.c_wchar_p]
        self.dll.Everything3_ConnectW.restype = ctypes.c_void_p

        self.dll.Everything3_DestroyClient.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_DestroyClient.restype = ctypes.c_bool

        self.dll.Everything3_Search.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.dll.Everything3_Search.restype = ctypes.c_void_p

        # Result list functions
        self.dll.Everything3_GetResultListCount.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_GetResultListCount.restype = ctypes.c_size_t

        self.dll.Everything3_GetResultFullPathNameW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_wchar_p,
            ctypes.c_size_t
        ]
        self.dll.Everything3_GetResultFullPathNameW.restype = ctypes.c_size_t

        self.dll.Everything3_DestroyResultList.argtypes = [ctypes.c_void_p]
        self.dll.Everything3_DestroyResultList.restype = ctypes.c_bool

        # Connect to Everything
        self.client = self.dll.Everything3_ConnectW(None)
        if not self.client:
            raise RuntimeError("Failed to connect to Everything")

    def search(self, pattern: str, offset: int = 0, count: int = 0) -> List[str]:
        """
        Perform a search and return list of full paths

        Args:
            pattern: Search pattern
            offset: Start index for results
            count: Maximum number of results (0 for unlimited)

        Returns:
            List of full paths for matching files/folders
        """
        # Set search parameters
        self.dll.Everything3_SetSearchTextW(self.search_state, pattern)

        # Set viewport parameters
        self.dll.Everything3_SetSearchViewportOffset(self.search_state, offset)
        self.dll.Everything3_SetSearchViewportCount(self.search_state, count)

        # Execute search
        result_list = self.dll.Everything3_Search(self.client, self.search_state)
        if not result_list:
            return []

        # Get results
        self.items = []
        self.num_results = self.dll.Everything3_GetResultListCount(result_list)

        if count > 0:
            _num = min(self.num_results, count)
        else :
            _num = self.num_results

        _path_buffer = ctypes.create_unicode_buffer(self.max_path)
        for _i in range(offset, _num):
            self.dll.Everything3_GetResultFullPathNameW(
                result_list,
                _i,
                _path_buffer,
                self.max_path
            )
            self.items.append(_path_buffer.value)

        # Cleanup result list
        self.dll.Everything3_DestroyResultList(result_list)

        return self.items

    def set_match_path(self, enable: bool) -> None:
        """Enable/disable path matching"""
        self.dll.Everything3_SetSearchMatchPath(self.search_state, enable)

    def set_match_case(self, enable: bool) -> None:
        """Enable/disable case sensitivity"""
        self.dll.Everything3_SetSearchMatchCase(self.search_state, enable)

    def set_match_whole_word(self, enable: bool) -> None:
        """Enable/disable whole word matching"""
        self.dll.Everything3_SetSearchMatchWholeWords(self.search_state, enable)

    def set_regex(self, enable: bool) -> None:
        """Enable/disable regex mode"""
        self.dll.Everything3_SetSearchRegex(self.search_state, enable)

    def set_match_diacritics(self, enable: bool) -> None:
        """Enable/disable diacritics matching"""
        self.dll.Everything3_SetSearchMatchDiacritics(self.search_state, enable)

    def set_match_prefix(self, enable: bool) -> None:
        """Enable/disable prefix matching"""
        self.dll.Everything3_SetSearchMatchPrefix(self.search_state, enable)

    def set_match_suffix(self, enable: bool) -> None:
        """Enable/disable suffix matching"""
        self.dll.Everything3_SetSearchMatchSuffix(self.search_state, enable)

    def set_ignore_punctuation(self, enable: bool) -> None:
        """Enable/disable punctuation ignoring"""
        self.dll.Everything3_SetSearchIgnorePunctuation(self.search_state, enable)

    def set_whitespace(self, enable: bool) -> None:
        """Enable/disable whitespace handling"""
        self.dll.Everything3_SetSearchWhitespace(self.search_state, enable)

    def set_folders_first(self, folders_first_type: int) -> None:
        """Set folders first type"""
        self.dll.Everything3_SetSearchFoldersFirst(self.search_state, folders_first_type)

    def set_request_total_size(self, enable: bool) -> None:
        """Enable/disable total size request"""
        self.dll.Everything3_SetSearchRequestTotalSize(self.search_state, enable)

    def set_hide_result_omissions(self, enable: bool) -> None:
        """Enable/disable hiding result omissions"""
        self.dll.Everything3_SetSearchHideResultOmissions(self.search_state, enable)

    def set_sort_mix(self, enable: bool) -> None:
        """Enable/disable sort mixing"""
        self.dll.Everything3_SetSearchSortMix(self.search_state, enable)

    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'search_state'):
            self.dll.Everything3_DestroySearchState(self.search_state)
        if hasattr(self, 'client'):
            self.dll.Everything3_DestroyClient(self.client)

if __name__ == "__main__":
    EVT = Everything3()

    # Set search modifiers if needed
    EVT.set_match_case(True)
    EVT.set_match_path(True)
    EVT.set_match_whole_word(True)
    EVT.set_regex(False)
    EVT.set_match_diacritics(True)
    EVT.set_match_prefix(True)
    EVT.set_match_suffix(False)
    EVT.set_ignore_punctuation(True)
    EVT.set_whitespace(True)
    EVT.set_folders_first(0)  # EVT3.FOLDERS_FIRST_ALWAYS constants
    EVT.set_request_total_size(True)
    EVT.set_hide_result_omissions(False)
    EVT.set_sort_mix(False)

    # Simple search
    results = EVT.search("*")
    if results:
        print(f'search phrase: "*", num: {EVT.num_results}')

    # Searches with options
    phrases = ["log.txt", "C:", "*.txt", "*.TXT"]
    for phrase in phrases:
        results = EVT.search(
            phrase,
            offset=0,
            count=100
        )
        if results:
            print(f'search phrase: "{phrase}", num: {EVT.num_results}, count: {len(EVT.items)}, first item: {EVT.items[1]}')
        else:
            print("nothing found")

