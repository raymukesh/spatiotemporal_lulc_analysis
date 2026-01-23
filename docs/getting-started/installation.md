# Installation

There are two ways to install the Spatiotemporal LULC Analysis plugin.

## Method 1: QGIS Plugin Manager (Recommended)

The easiest way to install the plugin is through the QGIS Plugin Manager:

1. Open QGIS (version 3.28 or higher)
2. Navigate to **Plugins** > **Manage and Install Plugins...**
3. Click on the **All** tab
4. Search for "**Spatiotemporal LULC Analysis**"
5. Select the plugin and click **Install Plugin**

!!! tip "Enable Experimental Plugins"
    If you don't see the plugin in the list, you may need to enable experimental plugins:

    1. Go to the **Settings** tab in the Plugin Manager
    2. Check **Show also experimental plugins**
    3. Return to the **All** tab and search again

## Method 2: Install from ZIP

If you prefer to install manually or want a specific version:

1. Download the latest release ZIP from the [GitHub Releases page](https://github.com/raymukesh/spatiotemporal_lulc_analysis/releases)
2. Open QGIS
3. Navigate to **Plugins** > **Manage and Install Plugins...**
4. Click on **Install from ZIP**
5. Browse to the downloaded ZIP file and click **Install Plugin**

## Method 3: Development Installation

For developers who want to contribute or modify the plugin:

```bash
# Clone the repository
git clone https://github.com/raymukesh/spatiotemporal_lulc_analysis.git

# Copy to QGIS plugins directory
# Windows:
copy spatiotemporal_lulc_analysis "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\"

# macOS:
cp -r spatiotemporal_lulc_analysis ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux:
cp -r spatiotemporal_lulc_analysis ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

After copying, restart QGIS and enable the plugin through the Plugin Manager.

## Verify Installation

After installation, verify the plugin is working:

1. Look for **Spatiotemporal LULC Analysis** in the **Plugins** menu
2. Click on it to open the analysis dock panel
3. The dock should appear on the right side of your QGIS window

!!! success "Installation Complete"
    If you see the dock panel with tabs for Inputs, Legend, Options, and Validation, the installation was successful.

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| QGIS | 3.28+ |
| Operating System | Windows, macOS, or Linux |
| Additional Dependencies | None |

The plugin has no external Python dependencies - all required libraries are either bundled or included with QGIS.

## Updating the Plugin

### Via Plugin Manager

1. Open **Plugins** > **Manage and Install Plugins...**
2. Go to the **Upgradable** tab
3. If an update is available, select the plugin and click **Upgrade Plugin**

### Manual Update

1. Uninstall the current version through Plugin Manager
2. Download and install the new version using the ZIP method

## Uninstallation

1. Open **Plugins** > **Manage and Install Plugins...**
2. Go to the **Installed** tab
3. Select **Spatiotemporal LULC Analysis**
4. Click **Uninstall Plugin**

## Next Steps

Now that you have the plugin installed, proceed to the [Quick Start](quickstart.md) guide to run your first analysis.
