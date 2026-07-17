### POSIX 信号量（`<semaphore.h>`）

```
#include <semaphore.h>
#include <pthread.h>
#include <stdio.h>

sem_t sem;

void* worker(void* arg) {
    sem_wait(&sem);   // P 操作，申请资源
    printf("Thread %ld working...\n", (long)arg);
    sleep(1);
    sem_post(&sem);   // V 操作，释放资源
    return NULL;
}

int main() {
    pthread_t t[5];
    sem_init(&sem, 0, 2); // 初始化，最多允许2个线程同时工作

    for (long i = 0; i < 5; i++) {
        pthread_create(&t[i], NULL, worker, (void*)i);
    }
    for (int i = 0; i < 5; i++) {
        pthread_join(t[i], NULL);
    }

    sem_destroy(&sem);
    return 0;
}
```