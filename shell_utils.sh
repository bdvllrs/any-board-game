#!/usr/bin/env sh

create() {
    GAME_NAME=$1
    USERNAME=$2

    RESPONSE=$(curl --header "Content-Type: application/json" \
        --request POST \
        --data "{\"username\":\"${USERNAME}\"}" \
        "http://localhost:8080/round/create/${GAME_NAME}")
    echo "Received:" $(echo $RESPONSE | jq)

    export GAME_ID=$(echo $RESPONSE | jq -r '.gameId')
    export PLAYER_ID_CREATOR=$(echo $RESPONSE | jq -r '.playerId')
}

join() {
    GAME_ID=$1
    USERNAME=$2

    RESPONSE=$(curl "http://localhost:8080/round/${GAME_ID}/join?username=${USERNAME}")
    echo "Received:" $(echo $RESPONSE | jq)

    export PLAYER_ID_LAST=$(echo $RESPONSE | jq -r '.playerId')
}

ws() {
    GAME_ID=$1
    PLAYER_ID=$2

    rlwrap -H ./.ws_history -- wscat --slash -P -c "ws://localhost:8080/round/${GAME_ID}/join?playerId=${PLAYER_ID}"
}

create_bataille() {
    create bataille x
    join $GAME_ID y
}

ws_creator() {
    ws $GAME_ID $PLAYER_ID_CREATOR
}

ws_last() {
    ws $GAME_ID $PLAYER_ID_LAST
}

debug_bataille() {
    create_bataille
    # set-option -g default-shell '/bin/bash' \
    tmux \
        new-session  "source ./shell_utils.sh && ws_creator ; read" \; \
        split-window "source ./shell_utils.sh && ws_last ; read" \; \
        select-layout even-horizontal
}
