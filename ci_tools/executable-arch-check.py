import os
import subprocess
import logging

# Set up logging with the specified format
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import subprocess
import logging

# Set up logging with the specified format
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_binary_architecture(filepath, debug=True):  # Set debug to True by default
    """
    Check if a binary file's architecture matches its directory name.
    
    Args:
        filepath: Path to the binary file
        debug: If True, print detailed debug information
        
    Returns:
        None if the file matches the expected architecture, otherwise the filepath
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Get the directory name
    dir_name = os.path.basename(os.path.dirname(filepath))
    
    logger.debug(f"Checking file: {filepath}")
    logger.debug(f"Directory name: {dir_name}")
    
    # Determine expected architecture from directory name
    expected_arch = None
    expected_os = None
    
    if "aarch64" in dir_name or "arm64" in dir_name:
        expected_arch = "aarch64"
        if "linux" in dir_name:
            expected_os = "linux"
        elif "apple" in dir_name or "darwin" in dir_name:
            expected_os = "macos"
    elif "x86_64" in dir_name:
        expected_arch = "x86_64"
        if "linux" in dir_name:
            expected_os = "linux"
        elif "windows" in dir_name:
            expected_os = "windows"
        elif "apple" in dir_name or "darwin" in dir_name:
            expected_os = "macos"
    
    if not expected_arch or not expected_os:
        raise ValueError(f"Could not determine expected architecture from directory: {dir_name}")
    
    logger.debug(f"Expected architecture: {expected_arch}")
    logger.debug(f"Expected OS: {expected_os}")
    
    # Check actual file architecture using the 'file' command
    try:
        file_output = subprocess.check_output(["file", filepath], 
                                            stderr=subprocess.STDOUT, 
                                            universal_newlines=True)
        
        logger.debug(f"File command output: {file_output}")
        
        # Check for Linux binaries
        if expected_os == "linux":
            # Check architecture - print each check result
            arch_terms = ["x86-64", "x86_64", "X86_64"]
            for term in arch_terms:
                logger.debug(f"Checking for '{term}' in file output: {term in file_output}")
            
            arch_match = False
            if expected_arch == "aarch64" and any(term in file_output for term in 
                                                ["ARM aarch64", "ARM64", "aarch64"]):
                arch_match = True
            elif expected_arch == "x86_64" and any(term in file_output for term in arch_terms):
                arch_match = True
                
            # Check OS - print each check result
            os_terms = ["ELF", "Linux", "GNU/Linux"]
            for term in os_terms:
                logger.debug(f"Checking for '{term}' in file output: {term in file_output}")
            
            os_match = any(term in file_output for term in os_terms)
            
            logger.debug(f"Linux - Architecture match: {arch_match}")
            logger.debug(f"Linux - OS match: {os_match}")
            
            if not (arch_match and os_match):
                logger.debug(f"Mismatch detected for Linux binary")
                return False
                
        # Check for Windows binaries
        elif expected_os == "windows":
            # Similar detailed logging for Windows...
            windows_terms = ["PE32+", "PE32", "MS Windows", "Windows", "Win32", "PE executable", "for MS Windows"]
            for term in windows_terms:
                logger.debug(f"Checking for '{term}' in file output: {term in file_output}")
            
            is_windows = any(term in file_output for term in windows_terms)
            
            arch_terms = ["x86-64", "x86_64", "X86_64", "PE32+", "64-bit", "Intel 80386"]
            for term in arch_terms:
                logger.debug(f"Checking for '{term}' in file output: {term in file_output}")
            
            arch_match = False
            if expected_arch == "x86_64" and any(term in file_output for term in arch_terms):
                arch_match = True
            elif expected_arch == "aarch64" and any(term in file_output for term in 
                                                  ["ARM64", "ARM aarch64", "aarch64"]):
                arch_match = True
                
            logger.debug(f"Windows - Is Windows: {is_windows}")
            logger.debug(f"Windows - Architecture match: {arch_match}")
            
            if not (is_windows and arch_match):
                logger.debug(f"Mismatch detected for Windows binary")
                return False
                
        # Check for macOS binaries
        elif expected_os == "macos":
            # Similar detailed logging for macOS...
            logger.debug(f"Checking for 'Mach-O' in file output: {'Mach-O' in file_output}")
            is_macos = "Mach-O" in file_output
            
            arch_match = False
            if expected_arch == "aarch64":
                arch_terms = ["arm64", "ARM64", "arm_64", "aarch64"]
                for term in arch_terms:
                    logger.debug(f"Checking for '{term}' in file output: {term in file_output}")
                arch_match = any(term in file_output for term in arch_terms)
            elif expected_arch == "x86_64":
                arch_terms = ["x86_64", "x86-64", "X86_64"]
                for term in arch_terms:
                    logger.debug(f"Checking for '{term}' in file output: {term in file_output}")
                arch_match = any(term in file_output for term in arch_terms)
                
            logger.debug(f"macOS - Is macOS: {is_macos}")
            logger.debug(f"macOS - Architecture match: {arch_match}")
            
            if not (is_macos and arch_match):
                logger.debug(f"Mismatch detected for macOS binary")
                return False
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running 'file' command: {e}")
        # If 'file' command fails, we can't determine the architecture
        return False
    
    # If we got here, all checks passed
    logger.debug("All checks passed!")
    return True


def find_bin_files_and_check_executable(directory):
    """
    Recursively searches a directory for '.bin' files and checks if they
    have executable permissions.  Returns the filepath of the first .bin
    file found *without* executable permissions.


    Returns:
    - The filepath of a .bin file without executable permission (failure).
    - None if all .bin files have executable permission (success) or if no
    .bin files are found.
    """
    failed_files = []
    logging.debug(f"Starting search in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".bin") or file.endswith(".exe"):
                filepath = os.path.join(root, file)
                logging.debug(f"Found executable file: {filepath}")
                if not check_binary_architecture(filepath, debug=False):
                    logging.info(f"File {filepath} does not match parent.")
                    failed_files.append(filepath)
                else:
                    logging.debug(f"File {filepath} matches parent.")

    return failed_files  # All .bin files have executable permission, or no .bin files

# Example usage:
if __name__ == "__main__":
    directory_to_search = os.environ["DIRECTORY_TO_CHECK"]  # Replace with your directory
    result = []
    result = (find_bin_files_and_check_executable(directory_to_search))
 

    if len(result) > 0:
        for file in result:
            print(f" - {file}")
    else:
        print("Success: All executable files have executable permission.")
