#include <stdio.h>
#include <stdlib.h>
#include <sys/select.h>
#include "rtc.h"
#include "pid.h"
#include "motor.h"
#include <sys/socket.h>
#include "socketserver.h"
#include <netinet/in.h>
#include "utils.h"

int main(int argc, char *argv[]) {
    // Initialize 
    int cant = 5;
    int max_fd;
    int i, fd_rtc, res, fd_socket;
    int fd_connected_socket = -1;
    fd_set readfds;
    struct timeval timeout = {1, 0};
    char read_buffer[1024] = {0};
    // Initialize motor with torque and velocity
    init_motor(255, 0.015, 15.0);
    //  Allocate memory
    int a = 0, b = 0;
    int* torque_t = &a;
    int* vel_t = &b;
    float *kp, *ki, *kd;
    float j=0.0, k=1.0, c=2.0;
    kp = &k;
    ki = &j;
    kd = &c;

    //  Initialize socket and wait for connection
    struct sockaddr_in address;
    fd_socket = socket_init(INADDR_ANY, 8080, &address);


    fd_rtc = rtc_init(2);
    //  Initialize pid with delta_t = 2 secs.
    init_pid(2, 255, 0);
    set_variables(1.0, 0.5, 1.0);

    while(1) {
        FD_ZERO(&readfds);
        FD_SET(fd_socket, &readfds);
        FD_SET(fd_rtc, &readfds);
        max_fd = fd_rtc + 1;
        if (fd_connected_socket != -1) {
            FD_SET(fd_connected_socket, &readfds);
            max_fd = fd_connected_socket + 1;
        }
        
        res = select(max_fd, &readfds, NULL, NULL, NULL);
        if (res < 0) {
            printf("Error on select");
            fflush(stdout);
            return 0;
        }
        //  Check interruption
        if (FD_ISSET(fd_rtc, &readfds)) {
            //  Read the interruption to clean
            rtc_tick();
            *vel_t = get_speed();
            compute_pid(10, torque_t, vel_t);
            set_torque(*torque_t);
            printf("Desired Speed: %d, Torque: %d, Speed: %d\n", 10, *torque_t, *vel_t);
            fflush(stdout);
        } 
        if (FD_ISSET(fd_socket, &readfds)) {
            //  Leer conexion entrante
            fd_connected_socket = get_connected_socket(fd_socket, &address);
            
        }
        if (FD_ISSET(fd_connected_socket, &readfds)) {
            //  Leer lo que entra en el socket
            res = recv(fd_connected_socket, read_buffer, 1024, 0);
            if (res < 0) {
                printf("Error while reading socket");
                return 0;
            } else {
                parse(read_buffer, vel_t, kp, ki, kd);
                printf("%d,%f,%f,%f", *vel_t, *kp, *ki, *kd);
            }
        }
        else {
            printf("%d", res);
            fflush(stdout);
        }
    }
    rtc_close();
    return 0;
}
