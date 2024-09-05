document.getElementById("scrape-form").addEventListener("submit", async function(event) {
    event.preventDefault();  // Prevent the form from submitting the traditional way

    const query = document.getElementById("query").value;
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");
    const submitButton = document.getElementById("submit-btn");

    // Clear previous messages and images
    resultDiv.textContent = '';
    resultDiv.style.color = '';
    document.getElementById("unprocessed-images").innerHTML = '';
    document.getElementById("processed-images").innerHTML = '';

    // Show loading indicator
    loadingDiv.classList.remove('hidden');
    submitButton.disabled = true;

    try {
        const response = await fetch("http://127.0.0.1:8000/start-task/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                "name": query
            })
        });

        const data = await response.json();
        if (response.ok) {
            resultDiv.textContent = data.message;
            resultDiv.style.color = "green";

            // Start polling for images after starting the task
            pollImages(query);
        } else {
            resultDiv.textContent = `Error: ${data.detail}`;
            resultDiv.style.color = "red";
        }
    } catch (error) {
        resultDiv.textContent = `Request failed: ${error.message}`;
        resultDiv.style.color = "red";
    } finally {
        // Hide loading indicator and re-enable the submit button
        loadingDiv.classList.add('hidden');
        submitButton.disabled = false;
    }
});

// Polling function to fetch images continuously
async function pollImages(query) {
    const unprocessedImagesDiv = document.getElementById("unprocessed-images");
    const processedImagesDiv = document.getElementById("processed-images");

    const unprocessedSet = new Set();
    const processedSet = new Set();

    const interval = setInterval(async () => {
        try {
            // Fetch unprocessed images
            const unprocessedResponse = await fetch(`http://127.0.0.1:8000/get-images/?query=${query}&type=unprocessed`);
            const unprocessedData = await unprocessedResponse.json();

            if (unprocessedResponse.ok && unprocessedData.images && unprocessedData.images.length > 0) {
                unprocessedData.images.forEach(imgUrl => {
                    if (!unprocessedSet.has(imgUrl)) {
                        unprocessedSet.add(imgUrl);
                        const imgElement = document.createElement('img');
                        imgElement.src = imgUrl;
                        unprocessedImagesDiv.appendChild(imgElement);
                    }
                });
            }

            // Fetch processed images
            const processedResponse = await fetch(`http://127.0.0.1:8000/get-images/?query=${query}&type=processed`);
            const processedData = await processedResponse.json();

            if (processedResponse.ok && processedData.images && processedData.images.length > 0) {
                processedData.images.forEach(imgUrl => {
                    if (!processedSet.has(imgUrl)) {
                        processedSet.add(imgUrl);
                        const imgElement = document.createElement('img');
                        imgElement.src = imgUrl;
                        processedImagesDiv.appendChild(imgElement);
                    }
                });
            }
        } catch (error) {
            console.error('Error fetching images:', error);
        }
    }, 3000);  // Poll every 3 seconds
}
