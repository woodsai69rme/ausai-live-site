Tutorials
=========

Getting Started Tutorial
------------------------

This tutorial will walk you through the basics of using YouTube Enhancement Tools.

Installation
~~~~~~~~~~~~

First, install the package using pip:

.. code-block:: bash

    pip install youtube-enhancement-tools

Alternatively, you can clone the repository and install it in development mode:

.. code-block:: bash

    git clone https://github.com/youtube-enhancement-tools/youtube-enhancement-tools.git
    cd youtube-enhancement-tools
    pip install -e .

Initial Setup
~~~~~~~~~~~~~

Before using the tools, you should run the interactive setup to configure your preferences:

.. code-block:: bash

    youtube-enhancement-tools --setup

This will prompt you to enter your API keys (optional) and set up your download/output directories.

Basic Usage
~~~~~~~~~~~

To process a single YouTube video:

.. code-block:: bash

    youtube-enhancement-tools --url "https://www.youtube.com/watch?v=your-video-id"

The tool will:
1. Extract video information
2. Check copyright compliance
3. Download the video
4. Auto-edit to remove silences
5. Optionally generate an AI summary if API keys are configured

Batch Processing
~~~~~~~~~~~~~~~~

To process multiple videos, create a text file with one URL per line:

.. code-block:: text

    https://www.youtube.com/watch?v=video1
    https://www.youtube.com/watch?v=video2
    https://www.youtube.com/watch?v=video3

Then run:

.. code-block:: bash

    youtube-enhancement-tools --batch-file urls.txt

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

You can customize the behavior by modifying the ``youtube_tools_config.json`` file:

.. code-block:: json

    {
      "settings": {
        "download_dir": "./downloads/",
        "output_dir": "./output/",
        "temp_dir": "./temp/",
        "default_quality": "720p",
        "batch_size": 5,
        "max_retries": 3,
        "timeout_seconds": 300,
        "auto_edit_settings": {
          "silent_threshold": 0.04,
          "video_speed": 1.25
        }
      }
    }

API Usage
~~~~~~~~~

You can also use the tools programmatically in your Python code:

.. code-block:: python

    from youtube_enhancement_tools.processors.video_processor import process_youtube_video
    from youtube_enhancement_tools.config.config_manager import load_config

    # Load configuration
    config = load_config()

    # Process a video
    success = process_youtube_video(
        url="https://www.youtube.com/watch?v=example",
        config=config
    )

    if success:
        print("Video processed successfully!")
    else:
        print("Video processing failed!")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Dependency Errors**: If you get errors about missing dependencies, make sure you have installed all required tools:

   .. code-block:: bash

       pip install -r requirements-enhanced.txt

2. **Permission Errors**: Make sure you have write permissions to your download and output directories.

3. **Rate Limiting**: If you're processing many videos, you might hit rate limits. The tool includes rate limiting to prevent this, but if you encounter issues, consider reducing the frequency of requests.

4. **Copyright Compliance**: If the tool stops processing due to copyright concerns, verify that you have the rights to use the content.

FAQ
~~~

Q: Can I use this tool commercially?
A: The tool is provided as-is. Please ensure you comply with YouTube's Terms of Service and respect copyright laws when using it.

Q: How do I update the tool?
A: Simply run ``pip install --upgrade youtube-enhancement-tools`` to get the latest version.

Q: Where are the processed videos saved?
A: Videos are saved to the directory specified in your configuration file, typically ``./output/`` by default.