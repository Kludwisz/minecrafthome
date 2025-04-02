import subprocess
import re
import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_highest_glibc_version(filepath):
    """
    Determine the highest glibc version that the given file depends on.
    Works for both dynamic and static binaries.
    
    Args:
        filepath (str): Path to the file to analyze
        
    Returns:
        int: The highest glibc version found as an integer (e.g., 2.38 -> 238),
             or 999 if no glibc dependency is found or if it's a macOS binary
    """
    logging.debug(f"Analyzing file: {filepath}")
    
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # First, check if it's an ELF file and not a macOS binary
    try:
        file_output = subprocess.check_output(
            ["file", filepath], universal_newlines=True
        )
        logging.debug(f"File command output: {file_output.strip()}")
        
        # Skip macOS binaries
        if "Mach-O" in file_output or "apple-darwin" in file_output:
            logging.info(f"Skipping macOS binary: {filepath}")
            return 999  # macOS binary, not relevant for glibc
            
        if "ELF" not in file_output:
            logging.info(f"Not an ELF binary: {filepath}")
            return 999  # Not an ELF binary
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running 'file' command: {e}")
        return 999
    
    highest_version = None
    
    # Try to extract Linux kernel version from ELF header for statically linked binaries
    kernel_version_match = re.search(r"for GNU/Linux (\d+\.\d+\.\d+)", file_output)
    if kernel_version_match:
        kernel_version = kernel_version_match.group(1)
        logging.debug(f"Found kernel version requirement: {kernel_version}")
        
        # Map kernel version to approximate glibc version
        kernel_to_glibc = {
            "2.6.32": 211,  # RHEL 6
            "3.2.0": 215,   # Debian 7
            "3.10.0": 219,  # RHEL 7
            "4.4.0": 223,   # Ubuntu 16.04
            "4.9.0": 225,   # Debian 9
            "4.15.0": 227,  # Ubuntu 18.04
            "4.19.0": 228,  # Debian 10
            "5.4.0": 231,   # Ubuntu 20.04
            "5.10.0": 233,  # Debian 11
            "5.15.0": 235,  # Ubuntu 22.04
            "6.1.0": 238    # Debian 12
        }
        
        # Find the closest kernel version that's less than or equal to our target
        target_kernel = tuple(map(int, kernel_version.split('.')))
        closest_glibc = None
        
        for k, v in kernel_to_glibc.items():
            k_tuple = tuple(map(int, k.split('.')))
            if k_tuple <= target_kernel and (closest_glibc is None or v > closest_glibc):
                closest_glibc = v
                logging.debug(f"Found closer kernel match: {k} -> glibc {v}")
        
        if closest_glibc is not None:
            highest_version = closest_glibc
            logging.info(f"Estimated glibc version from kernel: {highest_version}")
    else:
        logging.debug("No kernel version found in ELF header")
    
    # Method 1: Check the binary itself for GLIBC version strings
    logging.debug("Method 1: Checking binary for GLIBC version strings")
    try:
        # Use strings and grep to find GLIBC version strings
        strings_cmd = f"strings '{filepath}' | grep -E 'GLIBC_[0-9]+\\.[0-9]+'"
        logging.debug(f"Running command: {strings_cmd}")
        
        strings_output = subprocess.check_output(
            strings_cmd, shell=True, stderr=subprocess.DEVNULL, universal_newlines=True
        )
        
        # Find all GLIBC version references
        glibc_versions = re.findall(r"GLIBC_([0-9]+\.[0-9]+)", strings_output)
        
        if glibc_versions:
            logging.debug(f"Found GLIBC versions in binary: {glibc_versions}")
            
            # Convert to integer and find the highest
            for version in glibc_versions:
                # Convert "2.38" to 238
                version_parts = version.split('.')
                version_int = int(version_parts[0]) * 100 + int(version_parts[1])
                
                if highest_version is None or version_int > highest_version:
                    highest_version = version_int
                    logging.debug(f"New highest version from binary: {highest_version}")
        else:
            logging.debug("No GLIBC version strings found in binary")
    except (subprocess.CalledProcessError, ValueError) as e:
        logging.debug(f"Error checking binary for GLIBC strings: {e}")
    
    # Method 2: Use objdump to check for GLIBC version requirements
    logging.debug("Method 2: Using objdump to check for GLIBC version requirements")
    try:
        objdump_cmd = f"objdump -T '{filepath}'"
        logging.debug(f"Running command: {objdump_cmd}")
        
        objdump_output = subprocess.check_output(
            ["objdump", "-T", filepath], stderr=subprocess.DEVNULL, 
            universal_newlines=True
        )
        
        # Find all GLIBC version references
        glibc_versions = re.findall(r"GLIBC_([0-9]+\.[0-9]+)", objdump_output)
        
        if glibc_versions:
            logging.debug(f"Found GLIBC versions with objdump: {glibc_versions}")
            
            for version in glibc_versions:
                version_parts = version.split('.')
                version_int = int(version_parts[0]) * 100 + int(version_parts[1])
                
                if highest_version is None or version_int > highest_version:
                    highest_version = version_int
                    logging.debug(f"New highest version from objdump: {highest_version}")
        else:
            logging.debug("No GLIBC version strings found with objdump")
    except (subprocess.CalledProcessError, ValueError) as e:
        logging.debug(f"Error running objdump: {e}")
    
    # Method 3: Use readelf to check for GLIBC version requirements
    logging.debug("Method 3: Using readelf to check for GLIBC version requirements")
    try:
        readelf_cmd = f"readelf -a '{filepath}'"
        logging.debug(f"Running command: {readelf_cmd}")
        
        readelf_output = subprocess.check_output(
            ["readelf", "-a", filepath], stderr=subprocess.DEVNULL, 
            universal_newlines=True
        )
        
        # Look for any GLIBC references in the readelf output
        glibc_versions = re.findall(r"GLIBC_([0-9]+\.[0-9]+)", readelf_output)
        
        if glibc_versions:
            logging.debug(f"Found GLIBC versions with readelf: {glibc_versions}")
            
            for version in glibc_versions:
                version_parts = version.split('.')
                version_int = int(version_parts[0]) * 100 + int(version_parts[1])
                
                if highest_version is None or version_int > highest_version:
                    highest_version = version_int
                    logging.debug(f"New highest version from readelf: {highest_version}")
        else:
            logging.debug("No GLIBC version strings found with readelf")
    except (subprocess.CalledProcessError, ValueError) as e:
        logging.debug(f"Error running readelf: {e}")
    
    # Method 4: Check needed libraries with readelf -d
    logging.debug("Method 4: Checking needed libraries with readelf -d")
    try:
        readelf_d_cmd = f"readelf -d '{filepath}'"
        logging.debug(f"Running command: {readelf_d_cmd}")
        
        readelf_d_output = subprocess.check_output(
            ["readelf", "-d", filepath], stderr=subprocess.DEVNULL, 
            universal_newlines=True
        )
        
        # Check if libc.so.6 is among the needed libraries
        if "libc.so.6" in readelf_d_output:
            logging.debug("Binary requires libc.so.6")
            
            # If we haven't found a version yet, use a conservative default
            if highest_version is None:
                # Default to glibc 2.5 (205) as a conservative estimate for binaries 
                # that need libc but don't specify a version
                highest_version = 205
                logging.info("Using conservative default glibc 2.5 (205) for binary requiring libc")
    except (subprocess.CalledProcessError, ValueError) as e:
        logging.debug(f"Error running readelf -d: {e}")
    
    final_version = highest_version if highest_version is not None else 999
    logging.info(f"Final determined glibc version for {filepath}: {final_version}")
    return final_version

def crawl(directory, glibc_limit = 999):
    """
    Recursively searches a directory for '.bin' files and checks if they
    depend on glibc 2.27 or above.

    """
    failed_files = []
    logging.debug(f"Starting search in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            glibc_version = 0
            if file.endswith(".bin"):
                filepath = os.path.join(root, file)
                logging.debug(f"Found executable file: {filepath}")
                glibc_version = get_highest_glibc_version(filepath)
                if glibc_version > glibc_limit and glibc_version != 999:
                    logging.info(f"File {filepath} depends on glibc > {glibc_limit}. ({glibc_version})")
                    failed_files.append(f"{filepath} glibc_max: {glibc_version}")
                elif glibc_version == 999:
                    logging.info(f"Skipping file, error encountered. May or may not be a problem.")
                else:
                    logging.debug(f"File {filepath} depends on glibc {glibc_limit} or lower. (({glibc_version})")

    return failed_files


if __name__ == "__main__":
    dir_to_check = os.environ["DIRECTORY_TO_CHECK"]  # Replace with the actual path to your XML file
    glibc_limit = int(os.environ["GLIBC_LIMIT"])
    result = []
    result = (crawl(dir_to_check, glibc_limit ))

    if len(result) > 0:
        for file in result:
            print(f" - {file}")
    else:
        print("Success: All version.xml files look correct.")
