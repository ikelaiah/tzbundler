"""
get_latest_tz.py - IANA Time Zone Data Downloader

This module handles downloading and extracting the latest IANA timezone database.

The IANA timezone database is the authoritative source for time zone information
worldwide. It's updated several times per year when countries change their
time zone rules or daylight saving time policies.

The database is distributed as a compressed tar.gz file containing multiple
text files with time zone definitions in a custom format.

Key Functions:
- get_latest_tz_data(): Main function - downloads and extracts in one call
- get_latest_tz_zipped_data(): Downloads the tar.gz file
- extract_tz_data(): Extracts the downloaded archive

File Flow:
Internet → tzdata-latest.tar.gz → tzdata_raw/ directory → individual tzdata files
"""

import requests
import tarfile
import pathlib
import os

# =============================================================================
# CONFIGURATION - URLs and file paths
# =============================================================================

# IANA's official download URL for the latest timezone database
# This always points to the most recent release (e.g., 2025a, 2025b, etc.)
URL_IANA = "https://www.iana.org/time-zones/repository/tzdata-latest.tar.gz"

# Windows time zone mappings
# The official and authoritative mapping between IANA (Linux/UNIX) time zone IDs and Windows time zone IDs.
URL_WIN_ZONES = "https://raw.githubusercontent.com/unicode-org/cldr/main/common/supplemental/windowsZones.xml"

# Local filename for the downloaded archive
OUTPUT_FILE_IANA = "tzdata-latest.tar.gz"  

# Local filename for the downloaded Windows zones XML file
OUTPUT_FILE_WIN_ZONES = "windowsZones.xml"

# Directory where we'll extract the archive contents and store windows zones xml file
# This will contain files like: africa, asia, europe, zone1970.tab, version, etc.
EXTRACT_DIR = "tzdata_raw"

# =============================================================================
# DOWNLOAD FUNCTION - Get the latest windowsZones.xml from GitHub
# =============================================================================

def get_latest_win_zones() -> bool:
    """
    Download the latest Windows time zone mappings from Unicode CLDR repository.
    
    This file contains the official mapping between IANA time zone IDs and
    Windows time zone IDs, which is crucial for cross-platform compatibility.
    
    Returns:
        bool: True if download was successful, False if any error occurred
        
    Raises:
        No exceptions are raised - all errors are caught and logged
    """
    print(f"🌍 Downloading latest Windows time zone mappings from Unicode CLDR...")
    print(f"   Source: {URL_WIN_ZONES}")
    
    try:
        response = requests.get(url=URL_WIN_ZONES)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Save the content to a local file
        with open(pathlib.Path(EXTRACT_DIR, OUTPUT_FILE_WIN_ZONES), "wb") as file:
            file.write(response.content)

        print(f"✅ Download complete: {pathlib.Path(EXTRACT_DIR, OUTPUT_FILE_WIN_ZONES)}")
        return True
    
    except requests.RequestException as e:
        print(f"❌ Error downloading Windows zones: {e}")
        return False

# =============================================================================
# DOWNLOAD FUNCTION - Get the latest tzdata from IANA
# =============================================================================

def get_latest_tz_zipped_data() -> bool:
    """
    Download the latest timezone data archive from IANA.
    
    The IANA timezone database is updated whenever countries change their
    time zone rules. This function downloads the latest version as a
    compressed tar.gz file.
    
    The file is downloaded in chunks to handle large files efficiently
    and avoid loading the entire file into memory at once.
    
    Returns:
        bool: True if download was successful, False if any error occurred
        
    Raises:
        No exceptions are raised - all errors are caught and logged
    """
    print(f"🌍 Downloading latest timezone data from IANA...")
    print(f"   Source: {URL_IANA}")
    print(f"   Target: {OUTPUT_FILE_IANA}")
    
    try:
        # Make HTTP request with streaming enabled
        # stream=True means we download in chunks rather than all at once
        # This is important for large files and shows download progress
        response = requests.get(url=URL_IANA, stream=True)
        
        # Check if the HTTP request was successful (status code 200)
        # This will raise an exception if we got 404, 500, etc.
        response.raise_for_status()
        
        # Get file size from headers for progress tracking (if available)
        total_size = response.headers.get('content-length')
        if total_size:
            total_size = int(total_size)
            print(f"   Size: {total_size // 1024}KB")
        
        # Open local file for writing in binary mode
        with open(OUTPUT_FILE_IANA, "wb") as file:
            downloaded = 0
            
            # Download in 8KB chunks
            # This balances memory usage vs. number of write operations
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress if we know the total size
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Progress: {percent:.1f}% ({downloaded // 1024}KB)", end="")
        
        if total_size:
            print()  # New line after progress indicator
            
        print(f"✅ Download complete: {OUTPUT_FILE_IANA}")
        return True
    
    except requests.RequestException as e:
        # This catches all requests-related errors:
        # - ConnectionError: Network problems, DNS resolution fails
        # - HTTPError: Bad status codes (404, 500, etc.)
        # - Timeout: Request took too long
        # - TooManyRedirects: Redirect loop
        print(f"❌ Error downloading timezone data: {e}")
        print("   Possible causes:")
        print("   - No internet connection")
        print("   - IANA website is down")
        print("   - Firewall blocking the request")
        print("   - Proxy configuration issues")
        return False
        
    except IOError as e:
        # This catches file system errors:
        # - Disk full
        # - Permission denied
        # - Path doesn't exist
        print(f"❌ Error saving file: {e}")  
        print("   Check disk space and file permissions")
        return False


# =============================================================================
# EXTRACTION FUNCTION - Unpack the downloaded archive
# =============================================================================

def extract_tz_data() -> None:
    """
    Extract the downloaded timezone data archive.
    
    The tzdata archive contains many files in a specific format:
    - africa, asia, europe, etc.: Zone definitions by region
    - zone1970.tab: Metadata (country codes, coordinates)
    - version: Version string (e.g., "2025a")
    - README, theory.html: Documentation
    
    All files are extracted to the EXTRACT_DIR directory, overwriting
    any existing files from previous downloads.
    
    Returns:
        None - errors are printed but not raised
    """
    print(f"📦 Extracting timezone data archive...")
    
    # Verify the downloaded file exists before trying to extract
    if not os.path.exists(OUTPUT_FILE_IANA):
        print(f"❌ Archive {OUTPUT_FILE_IANA} does not exist.")
        print("   You need to download the file first using get_latest_tz_zipped_data()")
        return
    
    # Check file size to make sure download completed properly
    file_size = os.path.getsize(OUTPUT_FILE_IANA)
    if file_size == 0:
        print(f"❌ Archive {OUTPUT_FILE_IANA} is empty (0 bytes).")
        print("   The download may have failed. Try downloading again.")
        return
        
    print(f"   Source: {OUTPUT_FILE_IANA} ({file_size // 1024}KB)")
    print(f"   Target: {EXTRACT_DIR}/")
    
    # Create the extraction directory if it doesn't exist
    # exist_ok=True means don't error if directory already exists
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    try:
        # Open the tar.gz file for reading
        # "r:gz" means read mode with gzip compression
        with tarfile.open(OUTPUT_FILE_IANA, "r:gz") as tar:
            
            # Get list of files in the archive for logging
            members = tar.getnames()
            print(f"   Found {len(members)} files in archive:")
            
            # Show first few files as examples
            for i, name in enumerate(members[:5]):
                print(f"     - {name}")
            if len(members) > 5:
                print(f"     ... and {len(members) - 5} more files")
            
            # Extract all files to the target directory
            # This will overwrite existing files with same names
            tar.extractall(path=EXTRACT_DIR)
            
        print(f"✅ Extraction complete: {EXTRACT_DIR}/")
        
        # Verify extraction by checking for key files
        key_files = ["africa", "asia", "europe", "zone1970.tab", "version"]
        missing_files = []
        
        for filename in key_files:
            if not os.path.exists(os.path.join(EXTRACT_DIR, filename)):
                missing_files.append(filename)
        
        if missing_files:
            print(f"⚠️  Warning: Some expected files are missing: {missing_files}")
            print("   The archive may be incomplete or corrupted")
        else:
            print("✅ All expected files found")
    
    except tarfile.TarError as e:
        # This catches tar-specific errors:
        # - Corrupted archive
        # - Unsupported compression
        # - Truncated file
        print(f"❌ Error extracting timezone data: {e}")
        print("   Possible causes:")
        print("   - Archive file is corrupted")
        print("   - Download was interrupted")
        print("   - Unsupported archive format")
        print("   Try downloading the file again")
        
    except IOError as e:
        # This catches file system errors during extraction:
        # - Disk full
        # - Permission denied
        # - Path too long
        print(f"❌ Error writing extracted files: {e}")
        print("   Check disk space and directory permissions")


# =============================================================================
# MAIN FUNCTION - Complete download and extraction workflow
# =============================================================================

def get_latest_tz_data() -> bool:
    """
    Complete workflow: download and extract the latest timezone data.
    
    This is the main function that other modules should call. It handles
    the entire process of getting fresh timezone data from IANA.
    
    Workflow:
    1. Download tzdata-latest.tar.gz from IANA
    2. Extract the archive to tzdata_raw/ directory  
    3. Clean up the downloaded archive file
    4. Handle any errors gracefully
    
    Returns:
        bool: True if entire process succeeded, False if any step failed
        
    Side Effects:
        - Creates tzdata_raw/ directory with extracted files
        - Downloads and deletes tzdata-latest.tar.gz
        - Prints progress messages to console
    """
    print("🚀 Starting timezone data download and extraction...")
    print("=" * 60)
    
    # Step 1: Download the archive
    success = get_latest_tz_zipped_data()
    
    if success:
        print()  # Blank line for readability
        
        # Step 2: Extract the archive
        extract_tz_data()
        
        print()  # Blank line for readability

        # Step 3: Download Windows zones mapping
        win_success = get_latest_win_zones()
        if not win_success:
            print("⚠️  Warning: Could not download Windows time zone mapping (windowsZones.xml)")

        print("🧹 Cleaning up...")
        
        # Step 4: Clean up the downloaded archive
        # We don't need the .tar.gz file anymore since we've extracted it
        try:
            if os.path.exists(OUTPUT_FILE_IANA):
                os.remove(OUTPUT_FILE_IANA)
                print(f"   Deleted {OUTPUT_FILE_IANA}")
        except OSError as e:
            print(f"⚠️  Warning: Could not delete {OUTPUT_FILE_IANA}: {e}")
            print("   You can manually delete this file")
        
        print("=" * 60)
        print("✅ SUCCESS: Download and extraction complete!")
        print(f"📁 Timezone data is now available in: {EXTRACT_DIR}/")
        print()
        print("Key files extracted:")
        
        # Show what files are now available
        key_files = [
            ("version", "tzdata version (e.g., '2025a')"),
            ("africa", "African time zones"),
            ("asia", "Asian time zones"), 
            ("europe", "European time zones"),
            ("northamerica", "North American time zones"),
            ("southamerica", "South American time zones"),
            ("australasia", "Australian/Pacific time zones"),
            ("zone1970.tab", "Zone metadata (countries, coordinates)"),
            ("windowsZones.xml", "Windows time zone mappings"),
        ]
        
        for filename, description in key_files:
            filepath = os.path.join(EXTRACT_DIR, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  ✓ {filename:<15} - {description} ({size:,} bytes)")
            else:
                print(f"  ✗ {filename:<15} - MISSING")
        
        return True
        
    else:
        print("=" * 60)
        print("❌ FAILURE: Download failed, skipping extraction")
        
        # Clean up any partial files that might exist
        print("🧹 Cleaning up partial files...")
        
        try:
            # Remove the extraction directory if it exists but might be incomplete
            if os.path.exists(EXTRACT_DIR):
                # Only remove if it's empty (to avoid deleting user data)
                try:
                    os.rmdir(EXTRACT_DIR)
                    print(f"   Removed empty directory: {EXTRACT_DIR}")
                except OSError:
                    print(f"   Directory {EXTRACT_DIR} not empty, leaving it alone")
            
            # Remove any partial download file
            if os.path.exists(OUTPUT_FILE_IANA):
                os.remove(OUTPUT_FILE_IANA)
                print(f"   Removed partial download: {OUTPUT_FILE_IANA}")
                
        except OSError as e:
            print(f"⚠️  Warning during cleanup: {e}")
        
        print()
        print("Troubleshooting tips:")
        print("- Check your internet connection")
        print("- Try running the script again in a few minutes")
        print("- Check if your firewall is blocking the connection")
        print("- Verify the IANA website is accessible: https://www.iana.org/time-zones")
            
        return False


# =============================================================================
# SCRIPT ENTRY POINT - Allow running this file directly
# =============================================================================

if __name__ == "__main__":
    """
    Entry point when running this file directly from command line.
    
    Usage:
        python get_latest_tz.py
        
    This will download and extract the latest timezone data, then exit.
    """
    print("IANA Timezone Data Downloader")
    print("=" * 40)
    print()
    
    # Run the complete workflow
    success = get_latest_tz_data()
    
    # Exit with appropriate code for shell scripts
    exit(0 if success else 1)