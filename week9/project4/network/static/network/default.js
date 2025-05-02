document.addEventListener('DOMContentLoaded', function() {
    console.log("JavaScript file loaded correctly!");

    const currentPath = window.location.pathname;
    console.log("Current page URL:", currentPath);

    if (currentPath.startsWith("/profile/")) {
        console.log("On a profile page! Looking for Follow button...");
    }

    // Only run post submission code if the elements exist
    const submitButton = document.querySelector('#post_submit');
    const contentField = document.querySelector('#postContent');
    if (submitButton && contentField) {
        submitButton.disabled = true;

        contentField.addEventListener('input', () => {
            if (contentField.value.trim() === "") {
                submitButton.disabled = true;
            } else {
                submitButton.disabled = false;
            }
        });

        submitButton.addEventListener('click', (event) => {
            event.preventDefault();
            submit_post();
        });
    }

    // Attach follow button listener if it exists
    const followBtn = document.querySelector("#follow-btn");
    if (followBtn) {
        console.log("Follow button found in the DOM!");
        followBtn.addEventListener('click', (event) => {
            event.preventDefault();
            save_follow(followBtn);
        });
    } else {
        console.error("Follow button NOT found in the DOM");
    }

    // Only attach load page listener if the element exists
    const allPostsButton = document.querySelector('#All_posts_button');
    if (allPostsButton) {
        allPostsButton.addEventListener('click', (event) => {
            event.preventDefault();
            load_page("All Posts");
        });
    }
});


function load_page() {
    const allPostsDiv = document.querySelector('#All_posts');
    if (allPostsDiv) {
        allPostsDiv.style.display = 'block';
    } else {
        console.error('All_posts div not found.');

}};

function submit_post() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('Post submit button clicked, making API call...');

    const content = document.querySelector('#postContent').value;

    //Make API call and POST contents

    fetch('/post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            content: content
        })
    })

    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        //Check if the content is JSON
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json(); // Process response as JSON
        } else {
            throw new Error("Response not in JSON format");
        }
        

    })
        
    .then(result => {
        console.log('API response:', result); // Log the response from the server

        if (result.message === "Post successfuly made."){
            document.querySelector('#postContent').value = "";
            console.log("Successfuly made post")

            const allPostDiv = document.querySelector('#All_posts');
            const newPostDiv = document.createElement('div');

            newPostDiv.className = 'post mb-3';
            newPostDiv.innerHTML = `
                <div class="card p-3">
                    <h5>${result.poster}</h5>
                    <p>${result.contents}</p>
                    <small class="text-muted">${result.timestamp}></small>
                </div>
            `
            allPostsDiv.prepend(newPostDiv);

            //TODO: Successful post message appearing to user when post is made (Hussain, Oct 6, 2024 8:04PM)
            
        } else {
            console.error('Error:', result.error || 'Unknown error');
    }
})
    .catch(error => {
        console.error('Error in API call:', error);
    });

}

function save_follow(followBtn){
    console.log("Follow/Unfollow button clicked!");


    const username = window.location.pathname.split('/').pop();
    fetch(`/follow/${username}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })

    .then(response => response.json())

    .then(data => {
        if(data.message) {
            console.log(data.message);
            if (followBtn.textContent.trim() === "Follow"){
                followBtn.textContent = "Unfollow";
            } else {
                followBtn.textContent = "Follow";
            }
        }

        const followerCountElement = document.querySelector('#followers-count');
        if (followerCountElement) {
            let currentCount = parseInt(followerCountElement.textContent);
            followerCountElement.textContent = followBtn.textContent.trim() === "Follow"
                ? currentCount - 1
                : currentCount + 1;
        }
    })
    .catch(error => console.error('Error:', error));
}