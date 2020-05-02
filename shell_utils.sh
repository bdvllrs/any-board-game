#!/usr/bin/env sh

create() {
    readonly GAME_NAME=$1
    readonly USER_NAME=$2

    readonly RESPONSE=$(curl --header "Content-Type: application/json" \
        --request POST \
        --data "{\"username\":\"${USER_NAME}\"}" \
        "http://localhost:8080/round/create/${GAME_NAME}")
    jq <<< $RESPONSE

    export GAME_ID=$(echo $RESPONSE | jq -r '.gameId')
    export PLAYER_ID_CREATOR=$(echo $RESPONSE | jq -r '.playerId')
}

join() {
    readonly GAME_ID=$1
    readonly USER_NAME=$2

    readonly RESPONSE=$(curl "http://localhost:8080/round/${GAME_ID}/join?username=${USER_NAME}")
    jq <<< $RESPONSE

    export PLAYER_ID_LAST=$(echo $RESPONSE | jq -r '.playerId')
}

ws() {
    readonly GAME_ID=$1
    readonly PLAYER_ID=$2

    rlwrap wscat --slash -P -c "ws://localhost:8080/round/${GAME_ID}/join?playerId=${PLAYER_ID}"
}

create_bataille() {
    create bataille x
    join "$GAME_ID" y
}

ws_creator() {
    ws "$GAME_ID" "$PLAYER_ID_CREATOR"
}

ws_last() {
    ws "$GAME_ID" "$PLAYER_ID_LAST"
}

debug_bataille() {
    create_bataille
    # set-option -g default-shell '/bin/bash' \
    tmux \
        new-session  "source ./shell_utils.sh && ws_creator ; read" \; \
        split-window "source ./shell_utils.sh && ws_last ; read" \; \
        select-layout even-horizontal
}
