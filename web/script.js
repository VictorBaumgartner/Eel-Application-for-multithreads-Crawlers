document.addEventListener('DOMContentLoaded', () => {
    const remoteIpInput = document.getElementById('remoteIpInput');
    const outputDirInput = document.getElementById('outputDirInput');
    const concurrencyInput = document.getElementById('concurrencyInput');
    const depthInput = document.getElementById('depthInput');
    const fetchAndCrawlButton = document.getElementById('fetchAndCrawlButton');

    const machineNameSpan = document.getElementById('machineName');
    const totalStorageSpan = document.getElementById('totalStorage');
    const freeStorageSpan = document.getElementById('freeStorage');
    const cpuUsageSpan = document.getElementById('cpuUsage');
    const memoryUsageSpan = document.getElementById('memoryUsage');
    const crawlingStatusSpan = document.getElementById('crawlingStatus');
    const remoteServerMessageSpan = document.getElementById('remoteServerMessage');
    const crawlResultsPre = document.getElementById('crawlResults');

    let isCrawlingActive = false; // Tracks if the application is currently busy with fetching/crawling

    function updateMachineStatus() {
        eel.get_local_machine_metrics()().then(metrics => {
            if (metrics.status === "success") {
                machineNameSpan.textContent = metrics.machine_name;
                totalStorageSpan.textContent = metrics.total_storage_gb + " GB";
                freeStorageSpan.textContent = metrics.free_storage_gb + " GB";
                cpuUsageSpan.textContent = metrics.cpu_usage_percent + "%";
                memoryUsageSpan.textContent = metrics.memory_usage_percent + "%";

                crawlingStatusSpan.textContent = metrics.crawling_status === 'in_use' ? 'In Use' : 'Idle';
                crawlingStatusSpan.className = metrics.crawling_status === 'in_use' ? 'status-processing' : 'status-idle';
                
                // Update local 'isCrawlingActive' based on actual backend status
                isCrawlingActive = (metrics.crawling_status === 'in_use');

                // Disable/enable buttons based on processing status
                fetchAndCrawlButton.disabled = isCrawlingActive;

            } else {
                console.error("Error fetching machine metrics:", metrics.message);
                crawlingStatusSpan.textContent = 'Error';
                crawlingStatusSpan.className = 'status-error';
                remoteServerMessageSpan.textContent = `Error fetching local metrics: ${metrics.message}`;
                remoteServerMessageSpan.className = 'status-error';
            }
        }).catch(err => {
            console.error("Unhandled error fetching machine metrics:", err);
            crawlingStatusSpan.textContent = 'Error';
            crawlingStatusSpan.className = 'status-error';
            remoteServerMessageSpan.textContent = `Unhandled error: ${err.message || err}`;
            remoteServerMessageSpan.className = 'status-error';
        });
    }

    // Update machine status every 3 seconds
    setInterval(updateMachineStatus, 3000);
    updateMachineStatus(); // Initial update

    fetchAndCrawlButton.addEventListener('click', async () => {
        if (isCrawlingActive) {
            alert("The application is currently busy. Please wait.");
            return;
        }

        const remoteIp = remoteIpInput.value;
        const outputDir = outputDirInput.value;
        const maxConcurrency = parseInt(concurrencyInput.value);
        const maxDepth = parseInt(depthInput.value);

        if (!remoteIp || !outputDir) {
            alert("Please enter a valid Remote Server IP and Output Directory.");
            return;
        }
        if (isNaN(maxConcurrency) || maxConcurrency < 1) {
            alert("Max Concurrency must be a number greater than or equal to 1.");
            return;
        }
        if (isNaN(maxDepth) || maxDepth < 0) {
            alert("Max Depth must be a non-negative number.");
            return;
        }

        // Set initial UI state for fetching and crawling
        remoteServerMessageSpan.textContent = 'Requesting URLs from remote server...';
        remoteServerMessageSpan.className = ''; // Clear previous status classes
        crawlResultsPre.textContent = 'Fetching URLs...';
        isCrawlingActive = true;
        updateMachineStatus(); // Trigger immediate update to disable button

        try {
            const fetchResult = await eel.fetch_urls_from_remote_server(remoteIp)();

            if (fetchResult.status === "success" && fetchResult.urls.length > 0) {
                remoteServerMessageSpan.textContent = fetchResult.message;
                remoteServerMessageSpan.className = 'status-success';
                crawlResultsPre.textContent = 'Starting crawl with fetched URLs...';

                const crawlResult = await eel.start_crawl_process(
                    fetchResult.urls,
                    outputDir,
                    maxConcurrency,
                    maxDepth
                )();

                if (crawlResult.status === "error") {
                    crawlResultsPre.textContent = 'Crawl Failed: ' + crawlResult.message + '\n\n' + JSON.stringify(crawlResult, null, 2);
                    crawlResultsPre.className = 'status-error';
                    // Notify remote that processing finished with issues
                    await eel.notify_server_crawl_finished(remoteIp, false)();
                } else if (crawlResult.status === "completed") {
                    crawlResultsPre.textContent = 'Crawl Completed!\n\n' + JSON.stringify(crawlResult, null, 2);
                    crawlResultsPre.className = 'status-success';
                    // Notify remote that processing finished successfully
                    await eel.notify_server_crawl_finished(remoteIp, true)();
                } else {
                    crawlResultsPre.textContent = 'Crawl Finished with unexpected status.\n\n' + JSON.stringify(crawlResult, null, 2);
                    crawlResultsPre.className = 'status-error';
                    await eel.notify_server_crawl_finished(remoteIp, false)();
                }
            } else if (fetchResult.status === "success" && fetchResult.urls.length === 0) {
                remoteServerMessageSpan.textContent = `No URLs found on ${remoteIp}. ${fetchResult.message || 'Check remote server configuration.'}`;
                remoteServerMessageSpan.className = 'status-skipped';
                crawlResultsPre.textContent = 'No URLs to crawl.';
                crawlResultsPre.className = '';
            } 
            else {
                remoteServerMessageSpan.textContent = `Failed to fetch URLs: ${fetchResult.message}`;
                remoteServerMessageSpan.className = 'status-error';
                crawlResultsPre.textContent = `Failed to fetch URLs: ${fetchResult.message}`;
                crawlResultsPre.className = 'status-error';
            }
        } catch (e) {
            console.error("Error during fetch or crawl process:", e);
            remoteServerMessageSpan.textContent = `An unexpected error occurred: ${e.message || e}`;
            remoteServerMessageSpan.className = 'status-error';
            crawlResultsPre.textContent = `An unexpected error occurred: ${e.message || e}`;
            crawlResultsPre.className = 'status-error';
            // Attempt to notify remote of failure if the error was during crawl, not fetch connection
            if (e.message && e.message.includes("Crawl Failed")) {
                await eel.notify_server_crawl_finished(remoteIp, false)();
            }
        } finally {
            isCrawlingActive = false;
            updateMachineStatus(); // Final update to re-enable button
        }
    });
}); 