package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"
)

type Feedback struct {
	QQ       string    `json:"qq"`
	Feedback string    `json:"feedback"`
	Time     time.Time `json:"time"`
}

type Response struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data"`
}

// Worker pool size (limit the number of concurrent file writes)
const workerPoolSize = 30

// Channel for feedback items
var feedbackChannel = make(chan Feedback, 100)

func feedbackHandler(baseDir string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		// Parse the incoming JSON feedback
		var feedback Feedback
		err := json.NewDecoder(r.Body).Decode(&feedback)
		if err != nil {
			http.Error(w, "Failed to parse feedback", http.StatusBadRequest)
			return
		}

		feedback.Time = time.Now()

		// Create a response
		response := Response{
			Code:    1,
			Message: "Feedback received successfully",
			Data:    nil,
		}

		// Send the response back to the client
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, "Failed to send response", http.StatusInternalServerError)
			return
		}

		// Queue feedback for asynchronous processing
		feedbackChannel <- feedback
	}
}

// Asynchronous function to write feedback to a file with a date-based filename
func writeFeedbackToFile(baseDir string, feedback Feedback, wg *sync.WaitGroup) {
	defer wg.Done()

	// Ensure the directory exists
	err := os.MkdirAll(baseDir, os.ModePerm)
	if err != nil {
		log.Printf("Failed to create base directory: %v", err)
		return
	}

	// Get the current date to generate a unique file name
	currentDate := feedback.Time.Format("2006-01-02") // Format: YYYY-MM-DD
	feedbackFilePath := filepath.Join(baseDir, fmt.Sprintf("feedback_%s.txt", currentDate))

	// Open the feedback file
	file, err := os.OpenFile(feedbackFilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Printf("Failed to open feedback file: %v", err)
		return
	}
	defer func(file *os.File) {
		err := file.Close()
		if err != nil {
			log.Printf("Failed to close feedback file: %v", err)
		}
	}(file)

	// Write the feedback as a JSON string
	feedbackData, err := json.Marshal(feedback)
	if err != nil {
		log.Printf("Failed to marshal feedback: %v", err)
		return
	}

	// Write feedback to the file with a timestamp
	log.Printf("[%s]Writing feedback to file: %s", feedback.QQ, feedbackFilePath)
	_, err = fmt.Fprintf(file, "%s\n", feedbackData)
	if err != nil {
		log.Printf("Failed to write feedback to file: %v", err)
	}
}

func main() {
	// Create worker pool for handling feedback writing
	var wg sync.WaitGroup
	baseDir := "./feedback_files"

	// Start worker goroutines
	for i := 0; i < workerPoolSize; i++ {
		go func() {
			for feedback := range feedbackChannel {
				wg.Add(1)
				writeFeedbackToFile(baseDir, feedback, &wg)
			}
		}()
	}
    //     Mount the Static File Server

	http.Handle("/", http.FileServer(http.Dir("./dist")))

	// Start the HTTP server

	http.HandleFunc("/feedback", feedbackHandler(baseDir))
	port := ":8080"
	fmt.Printf("Server is running on http://localhost%s\n", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Could not start server: %s\n", err)
	}

	// Wait for all feedback to be processed before exiting
	wg.Wait()
}
