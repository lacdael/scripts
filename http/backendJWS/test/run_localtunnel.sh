#!/bin/bash

PORT=7070
DELAY=10
GIST_ID="c9778a4393eb560a59d998b868f3e317"
GITHUB_USERNAME="lacdael"
GITHUB_TOKEN=$GITHUB_TOKEN_GISTS

start_localtunnel() {
    echo "Starting localtunnel on port $PORT..."
    
    mkfifo lt_output_pipe
    (lt --port $PORT > lt_output_pipe 2>&1 &)

    while read -r line < lt_output_pipe; do
        URL=$(echo "$line" | grep -o 'https://[^ ]*')
        
        if [[ $URL ]]; then
            echo "Your URL is: $URL"
            update_gist "$URL"
        else
            echo "Failed to retrieve URL."
        fi
    done
    
    # Clean up
    rm lt_output_pipe
}

update_gist() {
    local url=$1
    echo "Updating Gist with URL: $url"
    # Create JSON payload for updating Gist content
    json="{\"files\":{\"url.txt\":{\"content\":\"$url\"}}}"
    curl -X PATCH -H "Authorization: token $GITHUB_TOKEN" \
         -d "$json" \
         "https://api.github.com/gists/$GIST_ID"
}

start_localtunnel
