document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const clubsList = document.getElementById("clubs-list");
  const studentEmailInput = document.getElementById("student-email");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  studentEmailInput.value = localStorage.getItem("student-email") || "";

  function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = type;
    setTimeout(() => messageDiv.classList.add("hidden"), 5000);
  }

  async function fetchActivities() {
    try {
      const email = encodeURIComponent(studentEmailInput.value.trim());
      const response = await fetch(`/activities?email=${email}`);
      if (!response.ok) throw new Error("Failed to load activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.replaceChildren(new Option("-- Select an activity --", ""));

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Club:</strong> ${details.club_name}</p>
          <p class="membership-state">${details.is_member ? "You are a member" : `Join ${details.club_name} to register`}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function fetchClubs() {
    try {
      const email = encodeURIComponent(studentEmailInput.value.trim());
      const response = await fetch(`/clubs?email=${email}`);
      if (!response.ok) throw new Error("Failed to load clubs");
      const clubs = await response.json();

      clubsList.innerHTML = clubs
        .map(
          (club) => `
            <div class="club-card">
              <h4>${club.name}</h4>
              <p>${club.description}</p>
              <p><strong>Category:</strong> ${club.category}</p>
              <p><strong>Contact:</strong> ${club.contact_info}</p>
              <button class="join-club-btn" type="button" data-club="${club.name}" ${club.is_member ? "disabled" : ""}>
                ${club.is_member ? "Joined" : "Join club"}
              </button>
            </div>
          `
        )
        .join("");

      clubsList.querySelectorAll(".join-club-btn").forEach((button) => {
        button.addEventListener("click", handleJoinClub);
      });
    } catch (error) {
      clubsList.innerHTML = "<p>Failed to load clubs. Please try again later.</p>";
      console.error("Error fetching clubs:", error);
    }
  }

  async function handleJoinClub(event) {
    const clubName = event.currentTarget.getAttribute("data-club");
    const email = studentEmailInput.value.trim();
    if (!studentEmailInput.reportValidity()) return;

    try {
      const response = await fetch(
        `/clubs/${encodeURIComponent(clubName)}/join?email=${encodeURIComponent(email)}`,
        { method: "POST" }
      );
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Could not join club");

      showMessage(result.message, "success");
      await Promise.all([fetchClubs(), fetchActivities()]);
    } catch (error) {
      showMessage(error.message || "Failed to join club. Please try again.", "error");
    }
  }

  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = studentEmailInput.value.trim();
    const activity = document.getElementById("activity").value;
    if (!studentEmailInput.reportValidity()) return;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  studentEmailInput.addEventListener("input", () => {
    localStorage.setItem("student-email", studentEmailInput.value);
  });
  studentEmailInput.addEventListener("change", () => {
    fetchClubs();
    fetchActivities();
  });

  fetchActivities();
  fetchClubs();
});
