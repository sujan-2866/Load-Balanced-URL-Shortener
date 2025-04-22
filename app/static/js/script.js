document.addEventListener("DOMContentLoaded", function () {
  const shortenForm = document.getElementById("shortenForm");
  const originalUrlInput = document.getElementById("originalUrl");
  const resultDiv = document.getElementById("result");
  const shortUrlInput = document.getElementById("shortUrl");
  const originalUrlDisplay = document.getElementById("originalUrlDisplay");
  const copyBtn = document.getElementById("copyBtn");
  const showAllBtn = document.getElementById("showAllBtn");
  const allUrlsDiv = document.getElementById("allUrls");
  const urlsTableBody = document.getElementById("urlsTableBody");
  const editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const editForm = document.getElementById("editForm");
  const editShortUrlInput = document.getElementById("editShortUrl");
  const editOriginalUrlInput = document.getElementById("editOriginalUrl");
  const saveUrlBtn = document.getElementById("saveUrlBtn");

  // Shorten URL form submission
  shortenForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const url = originalUrlInput.value.trim();

    try {
      const response = await fetch("/shorten/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url }),
      });

      const data = await response.json();

      shortUrlInput.value = data.short_url_link;
      originalUrlDisplay.textContent = data.original_url;
      resultDiv.classList.remove("d-none");

      // Scroll to result
      resultDiv.scrollIntoView({ behavior: "smooth" });
    } catch (error) {
      console.error("Error:", error);
      alert("Error shortening URL. Please try again.");
    }
  });

  // Copy button
  copyBtn.addEventListener("click", function () {
    shortUrlInput.select();
    document.execCommand("copy");

    copyBtn.textContent = "Copied!";
    setTimeout(() => {
      copyBtn.textContent = "Copy";
    }, 2000);
  });

  // Show all URLs
  showAllBtn.addEventListener("click", async function () {
    if (allUrlsDiv.classList.contains("d-none")) {
      try {
        const response = await fetch("/urls/");
        const data = await response.json();

        // Clear previous table content
        urlsTableBody.innerHTML = "";

        // Add URLs to table
        data.forEach((item) => {
          const row = document.createElement("tr");

          // Short URL cell
          const shortUrlCell = document.createElement("td");
          const shortUrlLink = document.createElement("a");
          shortUrlLink.href = item.short_url_link;
          shortUrlLink.textContent = item.short_url_link;
          shortUrlLink.target = "_blank";
          shortUrlLink.classList.add("short-url-link");
          shortUrlCell.appendChild(shortUrlLink);

          // Original URL cell
          const originalUrlCell = document.createElement("td");
          const originalUrlSpan = document.createElement("span");
          originalUrlSpan.textContent = item.original_url;
          originalUrlSpan.classList.add("original-url");
          originalUrlSpan.title = item.original_url;
          originalUrlCell.appendChild(originalUrlSpan);

          // Actions cell
          const actionsCell = document.createElement("td");

          const editBtn = document.createElement("button");
          editBtn.classList.add("btn", "btn-sm", "btn-primary", "me-2");
          editBtn.textContent = "Edit";
          editBtn.dataset.shortUrl = item.short_url;
          editBtn.dataset.originalUrl = item.original_url;
          editBtn.addEventListener("click", function () {
            editShortUrlInput.value = this.dataset.shortUrl;
            editOriginalUrlInput.value = this.dataset.originalUrl;
            editModal.show();
          });

          const deleteBtn = document.createElement("button");
          deleteBtn.classList.add("btn", "btn-sm", "btn-danger");
          deleteBtn.textContent = "Delete";
          deleteBtn.dataset.shortUrl = item.short_url;
          deleteBtn.addEventListener("click", async function () {
            if (confirm("Are you sure you want to delete this URL?")) {
              try {
                const response = await fetch(
                  `/delete/${this.dataset.shortUrl}`,
                  {
                    method: "DELETE",
                  }
                );

                if (response.ok) {
                  row.remove();

                  // If all rows deleted, hide table
                  if (urlsTableBody.children.length === 0) {
                    allUrlsDiv.classList.add("d-none");
                  }
                }
              } catch (error) {
                console.error("Error:", error);
                alert("Error deleting URL. Please try again.");
              }
            }
          });

          actionsCell.appendChild(editBtn);
          actionsCell.appendChild(deleteBtn);

          // Append cells to row
          row.appendChild(shortUrlCell);
          row.appendChild(originalUrlCell);
          row.appendChild(actionsCell);

          // Append row to table
          urlsTableBody.appendChild(row);
        });

        allUrlsDiv.classList.remove("d-none");
        allUrlsDiv.scrollIntoView({ behavior: "smooth" });
      } catch (error) {
        console.error("Error:", error);
        alert("Error fetching URLs. Please try again.");
      }
    } else {
      allUrlsDiv.classList.add("d-none");
    }
  });

  // Save edited URL
  saveUrlBtn.addEventListener("click", async function () {
    if (editForm.checkValidity()) {
      const shortUrl = editShortUrlInput.value;
      const newUrl = editOriginalUrlInput.value;

      try {
        const response = await fetch(`/update/${shortUrl}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: newUrl }),
        });

        if (response.ok) {
          // Close modal
          editModal.hide();

          // Update table if visible
          if (!allUrlsDiv.classList.contains("d-none")) {
            // Refresh the table
            showAllBtn.click();
            showAllBtn.click();
          }

          alert("URL updated successfully!");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Error updating URL. Please try again.");
      }
    } else {
      editForm.reportValidity();
    }
  });
});
