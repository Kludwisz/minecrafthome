import os
import subprocess
import logging

# Set up logging with the specified format
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_binary_architecture(filepath, debug=False):
    """
    Check if a binary file's architecture matches its directory name.
    
    Args:
        filepath: Path to the binary file
        debug: If True, print detailed debug information
        
    Returns:
        None if the file matches the expected architecture, otherwise the filepath
    """
    original_level = logger.level
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Get the directory name
    dir_name = os.path.basename(os.path.dirname(filepath))
    
    if debug:
        logger.debug(f"Checking file: {filepath}")
        logger.debug(f"Directory name: {dir_name}")
    
    # Determine expected architecture from directory name
    expected_arch = None
    expected_os = None
    
    if "aarch64" in dir_name or "arm64" in dir_name:
        expected_arch = "aarch64"
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
    
    if debug:
        logger.debug(f"Expected architecture: {expected_arch}")
        logger.debug(f"Expected OS: {expected_os}")
    
    # Check actual file architecture using the 'file' command
    try:
        file_output = subprocess.check_output(["file", filepath], 
                                            stderr=subprocess.STDOUT, 
                                            universal_newlines=True)
        
        if debug:
            logger.debug(f"File command output: {file_output}")
        
        # First, determine the actual architecture and OS from the file output
        actual_arch = None
        actual_os = None
        is_universal_binary = False
        
        # Check for macOS universal binary
        if "Mach-O universal binary" in file_output:
            actual_os = "macos"
            is_universal_binary = True
            
            # For universal binaries, check if the expected architecture is included
            if expected_arch == "aarch64" and any(term in file_output for term in ["arm64", "ARM64"]):
                actual_arch = "aarch64"  # The binary includes arm64
            elif expected_arch == "x86_64" and "x86_64" in file_output:
                actual_arch = "x86_64"  # The binary includes x86_64
            
            if debug:
                logger.debug(f"Detected universal binary with architectures: " + 
                           f"arm64: {'arm64' in file_output}, " +
                           f"x86_64: {'x86_64' in file_output}")
        else:
            # Regular binary detection
            # Check for architecture
            if any(term in file_output for term in ["ARM aarch64", "ARM64", "aarch64", "arm64"]):
                actual_arch = "aarch64"
            elif any(term in file_output for term in ["x86-64", "x86_64", "X86_64", "x86 64", "64-bit x86"]):
                actual_arch = "x86_64"
                
            # Check for OS
            if any(term in file_output for term in ["ELF", "Linux", "GNU/Linux"]):
                actual_os = "linux"
            elif any(term in file_output for term in ["PE32+", "PE32", "MS Windows", "Windows", "Win32", "PE executable", "for MS Windows"]):
                actual_os = "windows"
            elif "Mach-O" in file_output:
                actual_os = "macos"
            
        if debug:
            logger.debug(f"Detected architecture: {actual_arch}")
            logger.debug(f"Detected OS: {actual_os}")
            if is_universal_binary:
                logger.debug("This is a universal binary")
            
        # Compare expected with actual
        if expected_arch != actual_arch or expected_os != actual_os:
            if debug:
                logger.debug(f"Mismatch detected! Expected: {expected_arch}/{expected_os}, Actual: {actual_arch}/{actual_os}")
            return False
                
    except subprocess.CalledProcessError as e:
        if debug:
            logger.error(f"Error running 'file' command: {e}")
        # If 'file' command fails, we can't determine the architecture
        return False
    
    # If we got here, all checks passed
    if debug:
        logger.debug("All checks passed!")
    logger.setLevel(original_level)
    return True


def find_bin_files_and_check_executable(directory, debug=False):
    """
    Recursively searches a directory for '.bin' files and checks if they
    have executable permissions.  Returns the filepath of the first .bin
    file found *without* executable permissions.


    Returns:
    - The filepath of a .bin file without executable permission (failure).
    - None if all .bin files have executable permission (success) or if no
    .bin files are found.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    failed_files = []
    logger.debug(f"Starting search in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".bin") or file.endswith(".exe"):
                filepath = os.path.join(root, file)
                logger.debug(f"Found executable file: {filepath}")
                if not check_binary_architecture(filepath, debug=False):
                    logger.info(f"File {filepath} does not match parent.")
                    failed_files.append(filepath)
                else:
                    logger.debug(f"File {filepath} matches parent.")

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
