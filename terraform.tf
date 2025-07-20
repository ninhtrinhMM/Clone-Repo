terraform {					
	required_providers {				
		google = {			
			source = "hashicorp/google"		
			version = "4.80.0" // Provider version		
		}
	}				
	required_version = ">= 1.0" // Terraform version				
}					
// managing the infrastructure in GCP, this will					
// apply to all the resources in the project					
provider "google" {					
	project     = "project-ml-ops-01"				
	region      = "asia-southeast1"			
}					
// Google Kubernetes Engine					
resource "google_container_cluster" "my-gke" {					
	name     = "gke-ml-ops-01"				
	location = "asia-southeast1-a"
	network = "default"				
	// Tạo Node bên trong GKE				
	node_pool {				
		name = "node-mlops"			
		node_count = 3			
		node_config {	
			machine_type = "e2-medium"		
			disk_size_gb = 20		
				
		}			
	}
	remove_default_node_pool = true
	initial_node_count = 0 // Không tạo node pool mặc định, chỉ sử dụng node pool đã tạo ở trên				
}					
// Google Storage Bucket					
resource "google_storage_bucket" "my-bucket" {					
	name          = "bucket-store"			
	location      = "asia-southeast1" 		
	force_destroy = true				
	uniform_bucket_level_access = true				
}					
// Firewall					
resource "google_compute_firewall" "firewall-mlops"{					
	name    = "firewall-mlops"				
	network = "default"				
	allow {				
		protocol = "tcp"			
		ports    = ["5000", "30080", "3000", "9090"] // 9090: port của Prometheus
		                                             // 30080: port của Node Port Service  	
		                                             // 5000: port của app
		                                             // 3000: port của Grafana....		
	}		
	source_ranges = ["0.0.0.0/0"]   // allow all trafic: localhost			
}					