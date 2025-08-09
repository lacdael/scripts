#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

#define PATTERN_WIDTH 16
#define PATTERN_HEIGHT 8
#define NUM_STATES (1 << PATTERN_HEIGHT)

typedef struct { char note; int velocity; } Step;
typedef struct { Step grid[PATTERN_HEIGHT][PATTERN_WIDTH]; } DrumPattern;

int note_transitions[NUM_STATES][NUM_STATES] = {0};
unsigned int note_column_states[PATTERN_WIDTH] = {0};

typedef struct { unsigned int* velocity_states; int count; int capacity; } VelocityMap;
VelocityMap velocity_maps[NUM_STATES];

void cleanup_velocity_maps();

const char* default_pattern_str[PATTERN_HEIGHT] = {
    "----------------", "----------------", "----------------", "----------------",
    "----------------", "x-x-x-x-x-x-x-x-", "----X-------X---", "x---x---x---x---"
};

void parse_pattern_from_array(const char* pattern_str[PATTERN_HEIGHT], DrumPattern* pattern) {
    for (int i = 0; i < PATTERN_HEIGHT; i++) {
        for (int j = 0; j < PATTERN_WIDTH; j++) {
            char c = pattern_str[i][j];
            pattern->grid[i][j].note = c;
            if (c == 'x') pattern->grid[i][j].velocity = 1;
            else if (c == 'X') pattern->grid[i][j].velocity = 2;
            else pattern->grid[i][j].velocity = 0;
        }
    }
}

int parse_pattern_from_file(const char* filename, DrumPattern* pattern) {
    FILE* file = fopen(filename, "r");
    if (!file) { perror("Error opening file"); return 0; }
    char file_content[PATTERN_HEIGHT][PATTERN_WIDTH + 2];
    int lines_read = 0;
    while (lines_read < PATTERN_HEIGHT && fgets(file_content[lines_read], sizeof(file_content[0]), file)) {
        file_content[lines_read][strcspn(file_content[lines_read], "\n")] = 0;
        if (strlen(file_content[lines_read]) != PATTERN_WIDTH) {
             fprintf(stderr, "E: Line %d len mismatch (want %d, got %zu)\n", lines_read + 1, PATTERN_WIDTH, strlen(file_content[lines_read]));
             fclose(file); return 0;
        }
        lines_read++;
    }
    fclose(file);
    if (lines_read != PATTERN_HEIGHT) { fprintf(stderr, "E: File needs %d lines\n", PATTERN_HEIGHT); return 0; }
    const char* pattern_str_ptr[PATTERN_HEIGHT];
    for(int i=0; i<PATTERN_HEIGHT; i++) pattern_str_ptr[i] = file_content[i];
    parse_pattern_from_array(pattern_str_ptr, pattern);
    return 1;
}

void init_velocity_maps() {
    for (int i = 0; i < NUM_STATES; i++) {
        velocity_maps[i].velocity_states = NULL;
        velocity_maps[i].count = 0;
        velocity_maps[i].capacity = 0;
    }
    atexit(cleanup_velocity_maps);
}

void add_velocity_map(unsigned int note_state, unsigned int velocity_state) {
    VelocityMap* map = &velocity_maps[note_state];
    for (int i = 0; i < map->count; i++) if (map->velocity_states[i] == velocity_state) return;
    if (map->count >= map->capacity) {
        map->capacity = map->capacity == 0 ? 2 : map->capacity * 2;
        map->velocity_states = realloc(map->velocity_states, map->capacity * sizeof(unsigned int));
        if (!map->velocity_states) { perror("realloc"); exit(1); }
    }
    map->velocity_states[map->count++] = velocity_state;
}

void build_models_from_pattern(const DrumPattern* pattern) {
    unsigned int temp_velocity_states[PATTERN_WIDTH] = {0};
    for (int j = 0; j < PATTERN_WIDTH; j++) {
        unsigned int n_state = 0, v_state = 0;
        for (int i = 0; i < PATTERN_HEIGHT; i++) {
            if (pattern->grid[i][j].note != '-') {
                n_state |= (1 << i);
                if (pattern->grid[i][j].note == 'X') v_state |= (1 << i);
            }
        }
        note_column_states[j] = n_state;
        temp_velocity_states[j] = v_state;
    }
    for (size_t i = 0; i < PATTERN_WIDTH; i++) {
        add_velocity_map(note_column_states[i], temp_velocity_states[i]);
        if (i < PATTERN_WIDTH - 1) note_transitions[note_column_states[i]][note_column_states[i + 1]] = 1;
    }
}

int get_next_note_state(int previous_note_state) {
    int options[NUM_STATES], count = 0;
    for (int j = 0; j < NUM_STATES; j++) if (note_transitions[previous_note_state][j]) options[count++] = j;
    if (count > 0) return options[rand() % count];
    return note_column_states[rand() % PATTERN_WIDTH];
}

unsigned int get_random_velocity_state(unsigned int note_state) {
    VelocityMap* map = &velocity_maps[note_state];
    if (map->count > 0) return map->velocity_states[rand() % map->count];
    return 0;
}

void run_generation_loop(int interactive) {
    fprintf(stderr, "Generator running (interactive: %d)...\n", interactive);
    int previous_note_state = note_column_states[rand() % PATTERN_WIDTH];
    unsigned int step_count = 1;

    while (1) {
        if (interactive) {
            int c = getchar(); // Wait for a character (e.g., newline) from orchestrator
            if (c == EOF) break; // Exit if pipe closes
        }

        int current_note_state = get_next_note_state(previous_note_state);
        unsigned int current_velocity_state = get_random_velocity_state(current_note_state);

        printf("%04u: ", step_count++);
        for (int i = 0; i < PATTERN_HEIGHT; i++) {
            char c = '-';
            if ((current_note_state >> i) & 1) c = ((current_velocity_state >> i) & 1) ? 'X' : 'x';
            printf("%c", c);
        }
        printf("\n");
        fflush(stdout); // CRITICAL for piping

        previous_note_state = current_note_state;
        if (!interactive) usleep(125000);
    }
}

void print_pattern(const DrumPattern* pattern) {
    for (int i = 0; i < PATTERN_HEIGHT; i++) {
        for (int j = 0; j < PATTERN_WIDTH; j++) printf("%c", pattern->grid[i][j].note);
        printf("\n");
    }
}

void print_usage(const char* prog_name) {
    fprintf(stderr, "Usage: %s [-f <filename>] [-c | -i]\n", prog_name);
    fprintf(stderr, "  -f <filename>: Load pattern from file.\n");
    fprintf(stderr, "  -c           : Continuous auto-timed mode.\n");
    fprintf(stderr, "  -i           : Continuous interactive mode (waits for newline on stdin).\n");
}

void cleanup_velocity_maps() { for (int i = 0; i < NUM_STATES; i++) free(velocity_maps[i].velocity_states); }

int main(int argc, char *argv[]) {
    srand(time(NULL));
    init_velocity_maps();

    const char* filename = NULL;
    int mode = 0; // 0: print, 1: continuous, 2: interactive

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-f") == 0) {
            if (++i < argc) filename = argv[i];
            else { fprintf(stderr, "E: -f requires a filename.\n"); return 1; }
        } else if (strcmp(argv[i], "-c") == 0) mode = 1;
        else if (strcmp(argv[i], "-i") == 0) mode = 2;
        else { fprintf(stderr, "E: Unknown option '%s'.\n", argv[i]); print_usage(argv[0]); return 1; }
    }

    if (!filename && mode == 0) { print_usage(argv[0]); return 0; }

    DrumPattern pattern;
    if (filename) {
        if (!parse_pattern_from_file(filename, &pattern)) return 1;
    } else {
        parse_pattern_from_array(default_pattern_str, &pattern);
    }

    if (mode > 0) {
        build_models_from_pattern(&pattern);
        run_generation_loop(mode == 2);
    } else {
        print_pattern(&pattern);
    }

    return 0;
}
