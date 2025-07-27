# MỤC LỤC

1. [Giới thiệu tổng quát](#1-giới-thiệu-tổng-quát)
2. [Chuẩn bị](#2-chuẩn-bị)
3. [Khởi tạo Cluster GCP bằng Terraform](#3-Khởi-tạo-Cluster-GCP-bằng-Terraform)
4. [Khởi tạo Jaeger Tracing](#4-Khởi-tạo-Jaeger-Tracing)
5. [Khởi tạo Github Repo](#5-Khởi-tạo-Github-Repo)
6. [Thiết lập Jenkins](#6-Thiết-lập-Jenkins)
7. [Thiết lập liên kết giữa Jenkins với các platform khác](#7-Thiết-lập-liên-kết-giữa-Jenkins-với-các-platform-khác)
8. [Khởi tạo luồng Jenkins CICD](#8-Khởi-tạo-luồng-Jenkins-CICD)
9. [Các hệ thống giám sát](#9-Các-hệ-thống-giám-sát)
-------------------------------------------------------------------------------------

## 1. Giới thiệu tổng quan:

### a. Tổng quan về mô hình ML và mục đích triển khai hệ thống ML-prediction: 
- Mô hình Machine Learning trong Github Repo được huấn luyện với bộ dữ liệu chứa 45.000 bản ghi về người đăng ký vay vốn, với nhiều thuộc tính khác nhau liên quan đến:
  - Thông tin nhân khẩu học cá nhân về trình độ học vấn, thói quen tiêu dùng,...
  - Tình hình tài chính
  - Chi tiết khoản vay
- Bộ dữ liệu được sử dụng cho:
  - Mô hình hóa dự đoán
  - Đánh giá rủi ro tín dụng
  - Dự đoán khả năng vỡ nợ
- Mô hình được Data Preprocessing bởi các phương pháp Label Encoding, Standard Scaler và sử dụng phương pháp GridsearchCV để tìm ra Hyper Parameter tốt nhát cho model. Kết quả là model đạt được Metric Accuracy lên đến 93%.  
- Sau khi train model thành công, chúng ta triển khai model trên hệ thống Cluster (cụm máy) của Google Cloud Platform, vận hành và xây dựng bởi luồng CI/CD Jenkins tự động tích hợp với Cloud K8S để nhận request từ người dùng.

### **b. Sơ đồ Architecture System:**  

<img width="4286" height="2703" alt="Image" src="https://github.com/user-attachments/assets/27441b99-d966-4017-bd37-6d68249f3a1b" />  

### **c. Các công cụ cần cài đặt sẵn trên hệ điều hành Ubuntu:** 

- Gcloud CLI
- Git
- Kubectl
- Ngrok
- Terraform
- Helm
  
## 2. Chuẩn bị

### a. Kéo Repo (Kho chứa các file và folder) trên Github về:  

Mở Terminal ( Ctrl + Alt +T ) và gõ lần lượt các lệnh sau: 
- ```git init```
- ```git clone https://github.com/ninhtrinhMM/15-7-25-MLops-01-Deploy-Bank-Loan-Prediction-model```
- Ngay sau đó toàn bộ Github Repo từ link trên sẽ được tải về và hiển thị trong Folder tên là 15-7-25-MLops-01-Deploy-Bank-Loan-Prediction-model ở máy local, được gọi là Repo local.
- Mở VS Code và open Folder trên.

### b. Cấu trúc của Github Repo

<img width="806" height="390" alt="Image" src="https://github.com/user-attachments/assets/ec751f78-10fa-4811-9da8-8944566b5dec" />  

## 3. Khởi tạo Cluster GCP bằng Terraform

Truy cập vào https://console.cloud.google.com/ và đăng nhập bằng tài khoản Google.  

Click vào My First Project → chọn "New Project" để tạo Project mới.  

<img width="1033" height="54" alt="Image" src="https://github.com/user-attachments/assets/a61fa180-a3b1-4e5b-8345-9e4d612e2905" />  

**Lưu ý khi điền tên của Project phải trùng với tên Project của phần provider “google” trong file Terraform.**  

<img width="579" height="313" alt="Image" src="https://github.com/user-attachments/assets/b84d9d3e-d6a5-4646-a648-a24b6ace13b1" />  

Tạo xong project, trở lại VS Code, chạy Termianl command sau: ```gcloud auth login``` và chọn tài khoản Google cá nhân.  

Tạo config cho Gcloud lấy đúng Project: ```gcloud config set project <Tên Project trong file Terraform>```  

Tạo Application Default Credentials cho Terraform: ```gcloud auth application-default login``` và chọn lại đúng tài khoản Google cá nhân.  

Khởi động các APIs cần thiết bằng 3 command sau:  
```gcloud services enable compute.googleapis.com```  
```gcloud services enable container.googleapis.com```  
```gcloud services enable storage.googleapis.com```  
Chạy các lệnh sau để kiểm tra Terraform đã sẵn sàng và syntax trong file Terraform chưa:  
```terraform init```  
```terraform plan```  
Chạy file Terraform: ```terraform apply```, sau đó chọn "Y".  
Sau khi chạy xong, truy cập https://console.cloud.google.com/ --> My First Project --> <Tên Project trong file Terraform> --> Kubenetes Engines --> Cluster để kiểm tra   

<img width="1033" height="539" alt="Image" src="https://github.com/user-attachments/assets/ceffd75e-a224-43be-a3fe-776306e76fb3" />  

Nếu thấy tên của Cluster trùng với tên Cluster được thiết lập trong file Terraform nghĩa là thành công tạo 1 cụm máy Cluster, bên trong có 3 máy ảo VM Instance có cấu hình là E2 Medium.  

<img width="928" height="456" alt="Image" src="https://github.com/user-attachments/assets/2c0ff572-2368-48a4-a709-06a4e47d3897" />  
<img width="503" height="307" alt="Image" src="https://github.com/user-attachments/assets/fc71fe0a-2b1f-440f-9303-3a46c3e8c655" />  

## **4. Khởi tạo Jaeger Tracing:**  

Vì Jaeger là 1 công cụ theo dõi Trace được định nghĩa sẵn trong file ML-app.py (file main) nên chúng ta cần triển khai Jaegar trước có thể theo dõi Trace ngay khi app khởi động.  

Trước hết đảm bảo đã kết nối tới Cluster được tạo ở bước trước bằng command sau:  

```gcloud container clusters get-credentials <Tên Cluster> --zone <Nơi đặt máy> --project <Tên Project>```  

<img width="835" height="255" alt="Image" src="https://github.com/user-attachments/assets/cf3ccc49-92f4-4c9d-983e-5695e50ad74f" />  

Vì jaegar-deployment.yaml có setup năm trong namespace "monitoring" nên trước khi chạy file, ta cần thiết lập namespace "monitoring" trước và thực thi file jaegar-deployment.yaml sau bằng command sau:  

```kubectl create namespace monitoring && kubectl apply -f jaegar-deployment.yaml```  

Chạy xong, kiểm tra bằng command: ```kubectl get pod -n monitoring``` và ```kubectl get svc -n monitoring```  

Để truy cập được vào Jaeger, sử dụng port-forward: ```kubectl port-forward -n monitoring svc/jaeger 16686:16686``` sau đó truy cập vào localhost:16686, nếu thấy giao diện Jaeger hiện lên tức thành công.  

<img width="960" height="524" alt="Image" src="https://github.com/user-attachments/assets/1eb5169d-8581-4bbe-94ef-a552b6af305f" />    

**NOTE: Tất cả các thao tác mới với Terminal phải làm trên Terminal mới. Terminal hiện tại là để chứa Log của Jaeger.**  

<img width="474" height="147" alt="Image" src="https://github.com/user-attachments/assets/15dd48c4-9252-468c-bdcd-9f732f8b4e5e" />  

**NOTE: Để Jaeger có thể tracing được service của app, phải setup jaeger_exporter trong app.py chứa agent_host_name được tạo từ đúng namespace của service trong Cluster** 

## **5. Khởi tạo Github Repo**  
Truy cập github.com, tạo tài khoản nếu chưa có và khởi tạo 1 Repository ( Kho lưu trữ các file ) mới, điền Repository Name và để ở chế độ **PUBLIC**.   

<img width="327" height="148" alt="Image" src="https://github.com/user-attachments/assets/8c25622d-d712-48f0-ab1d-3edbbfc86ed6" />  

Trở về VS Code, chạy lệnh: ```git add .``` để add tất cả các Folder hiện tại vào Stageing Area.  
Chạy lệnh: ```git commit -m <Tên commit>``` để tạo 1 bản ghi Commit mới.  
Chạy lệnh: ```git remote add origin <Link Github Repo bạn vừa mới tạo>``` để tạo 1 remote tên origin nhằm liên kểt Repo dưới Local (toàn bộ file và folder đang được mở bằng VS Code) với Github Repo mới của bạn.  

Đồng hóa ( Synchronize ) giữa Repo dưới Local với Github repo của bạn: ```git push -u origin main```   

Từ giờ khi có 1 Commit mới được tạo ra thì để đẩy lên Github Repo chỉ cần chạy ```git push```  

## 6. Thiết lập Jenkins

### a. Khởi tạo Jenkins ở local  

Jenkins có vai trò tự động hóa trong các bước Test-kiểm, Build và Deploy- Triển khai. Để chạy Jenkins, chắc chắn đang ở trong thư mục Repo local:  

```cd ~/<Path repo>```

```docker compose -f jenkins-compose.yaml up -d```

Trong quá trình khởi tạo Container, sẽ hiện ra Password như sau dùng để đăng nhập Jenkins, copy và lưu lại. Nếu không hiển thị như trong ảnh trên, vào Container Jenkins bằng command sau: ```docker logs <tên container>```  để thấy được Password.

<img width="942" height="294" alt="Image" src="https://github.com/user-attachments/assets/e7c59994-f456-45a3-8ce3-f5c76e4811cf" />  

Tiếp theo truy cập vào Jenkins bằng cách vào http://localhost:8080 và nhập Password ban nãy xong chọn Continue.  

<img width="882" height="566" alt="Image" src="https://github.com/user-attachments/assets/10c339e0-48f0-462d-a9e1-04bb5399ab22" />  

Tiếp theo chọn Install Suggested Plugin ( Sử dụng hệ điều hành Ubuntu sẽ đỡ dính fail cài đặt hơn là Windown ) và chờ cài đặt hoàn tất.    

<img width="882" height="566" alt="Image" src="https://github.com/user-attachments/assets/d7265985-f2f1-406e-83d5-6c42744615b9" />  

Sau khi cài đặt các Plugin đề xuất xong, Popup đăng ký tên và password hiện lên, chọn Skip as admin.  

<img width="892" height="576" alt="Image" src="https://github.com/user-attachments/assets/02ced131-6847-4297-9fab-af60dd94ed83" />  

Xong chọn Save and Finish --> Start using Jenkins.  

<img width="882" height="332" alt="Image" src="https://github.com/user-attachments/assets/3ef433bf-52c8-4368-b094-3f6b1a8f897a" />   

Đăng nhập Jenkins thành công với tên tài khoản là admin, password đã được lưu. 

<img width="1289" height="558" alt="Image" src="https://github.com/user-attachments/assets/e0b9eb2c-c083-4ac0-9d20-448c1eca6af6" />  

Vào Manage Jenkins --> Plugin --> Availabale Plugins và search rồi cài đặt các Plugin cần thiết như:  
* Docker
* Docker Pipeline
* Docker Slaves
* Kubenetes
* Kubenetes CLI
* Kubenetes Credential

<img width="1271" height="421" alt="Image" src="https://github.com/user-attachments/assets/bf144381-0475-4a59-94a2-15eebd990bd7" />  
<img width="931" height="406" alt="Image" src="https://github.com/user-attachments/assets/734fa365-3b66-4b4c-8a2f-dac1a4b1b5cd" />  

### b. Kết nối Github Repo với Jenkins:  

Trước hết cần kết nối Github Repo với Jenkins để mỗi lần Github Repo được đẩy Commit mới hoặc tạo Branch (nhánh) mới thì Jenkins có thể nhận biết được và triển khai luồng CI/CD. Chúng ta sử dụng Webhook API.  
Trước hết sử dụng công cụ Ngrok để tạo 1 đường hầm Pubic cho Jenkins dưới Local. Truy cập page https://dashboard.ngrok.com/ và đăng nhập (tạo tài khoản nếu chưa có). Sau đó vào "Your Authtoken", chúng ta sẽ thấy token authen và copy đoạn mã token này.   

<img width="894" height="439" alt="Image" src="https://github.com/user-attachments/assets/2674bf58-6d92-496a-8360-035b2ef19c67" />  
<img width="692" height="167" alt="Image" src="https://github.com/user-attachments/assets/f2ff36a0-66a7-403f-8520-3a5760419540" />  

Bật Terminal của Vs code và chạy command: ```ngrok config add-authtoken <AUTHTOKEN lúc nãy>```  
Tiếp theo chạy: ```ngrok http 8080``` ( 8080 là Port của Jenkins )
Xong khu vực Terminal sẽ hiển thị giao diện như sau:  

<img width="818" height="319" alt="Image" src="https://github.com/user-attachments/assets/9ef74fc9-90ff-409d-92f1-bc352edc9736" />

Đoạn khoanh đỏ trong hình chính là địa chỉ web kết nối trực tiếp ( Tạo thành 1 "đường hầm" ) với Jenkins ở máy local, thay vì truy cập vào localhost:8080, chúng ta có thể truy cập Jenkins thông qua địa chỉ web này. Tiến hành copy địa chỉ web trên.  
Trở lại Github Repo, chọn Setting  

<img width="838" height="143" alt="Image" src="https://github.com/user-attachments/assets/d2ad92ba-e844-42de-9923-96dbab305f42" />  

Chọn Webhook --> Add Webhook  

<img width="1059" height="563" alt="Image" src="https://github.com/user-attachments/assets/2fa0e13e-911c-475b-b3f4-fa9ef0953b0b" />  

Giao diện Add Webhook hiện ra, phần Payload URL* điền link địa chỉ web lúc nãy kèm theo đuôi "/github-webhook/" để Jenkins nhận biết Webhook API. Phần Content Type* để Application Json.  

<img width="990" height="439" alt="Image" src="https://github.com/user-attachments/assets/70424728-2fb1-4167-a6e5-0c9e44ada9cb" />

Phần Which events would you like to trigger this webhook? chọn "Let me select individual events." và tích chọn Push ( hoặc nếu muốn có thể chọn cả Pull ) để Jenkins nhận biết 2 dạng sự kiện thay đổi này từ Github. Xong kéo xuống chọn "Add Webhook"  

<img width="609" height="397" alt="Image" src="https://github.com/user-attachments/assets/ce9cf452-736c-4ee0-8abc-5a23f380489a" />  

Hoàn thành Add Webhook API của Jenkins cho Github. Mở 1 Terminal mới ở VS Code, thử nghiệm tạo 1 commit mới dưới Repo Local và đẩy commit đó lên Github Repo. Nếu thấy tích xanh nghĩa là Webhook API đã hoạt động tốt.  

<img width="1000" height="402" alt="Image" src="https://github.com/user-attachments/assets/042522c2-a6ac-4400-b0cd-cf41c644e7c2" />  

## **7. Thiết lập liên kết giữa Jenkins với các platform khác**  

### a. Kết nối Jenkins với Dockerhub:  
   
Đầu tiên lấy Dockerhub Access Token, truy cập https://hub.docker.com/, click vào biểu tượng tài khoản và chọn Account Setting --> Personal Access Token --> Generate New Token --> Điền tên và chọn ngày hết hạn --> Chọn "Generate"  

<img width="684" height="439" alt="Image" src="https://github.com/user-attachments/assets/510a84b4-6db1-4008-868e-7f4bd4d83fbc" />  

Đoạn mã khoanh đỏ chính là Dockerhub Access Token. Copy và lưu Dockerhub Access Token.  

<img width="591" height="529" alt="Image" src="https://github.com/user-attachments/assets/918fa120-da57-4810-aeda-0b4a37c12675" />   

Để Jenkins có thể truy cập vào Dockerhub thực hiện các tác vụ, chúng ta cần tạo 1 Credential ( *Credential là tấm thẻ để truy cập vào nền tảng khác* ) để Jenkins có thể truy cập vào Dockerhub.  
Trở lại Jenkins, chọn Manage Jenkins --> Credential --> Click vào "system"  

<img width="856" height="320" alt="Image" src="https://github.com/user-attachments/assets/0b48619b-f67c-46c4-86e1-abebd9fffd8e" />  

Xong chọn tiếp "Global credentials (unrestricted)" --> Add Credentials  

<img width="1043" height="212" alt="Image" src="https://github.com/user-attachments/assets/1916705f-9912-4781-8ef6-10552e6385d8" />  
<img width="1201" height="227" alt="Image" src="https://github.com/user-attachments/assets/8f1f2e00-481d-4182-aa15-847c6df9a367" />  

Bảng New Credential hiện lên, lần lượt điền các thông tin như sau:  
1. User name = Tên tài khoản Dockerhub. 
2. Password chính là Dockerhub Access Token vừa nãy lưu.  
3. Điền ID cho Credential, ID này dùng để xác định chính xác Credential nào Jenkins sẽ sử dụng.  

<img width="1189" height="607" alt="Image" src="https://github.com/user-attachments/assets/a2b1767f-6c03-470f-80ff-d59935849c02" />  

XOng ấn "Create" để tạo Dockerhub Credential. Trở lại Manage Jenkins/Credential và thấy Credential hiện lên như trong hình dưới nghĩa là tạo thành công.  

<img width="1111" height="368" alt="Image" src="https://github.com/user-attachments/assets/2f5236d0-007a-4c72-ab9e-7d26195077d2" />  

### b. Kết nối Jenkins với GCP Cluster:  
Để Jenkins có thể truy cập vào chính xác cụm máy Cluster mà chúng ta tạo ở mục 3, trở về trang chủ Jenkins --> Manage Jenkins --> Clouds --> New Cloud. Sau đó điền tên cho Cloud và chọn type là Kubenetes xong nhấn "Create".  

<img width="896" height="353" alt="Image" src="https://github.com/user-attachments/assets/af5bac3e-d569-46f2-8d00-ec024cab129f" />  

Bảng New Cloud hiện lên, với các ô cần điền như **Kubenetes URL** và **Kubernetes server certificate key** và Credential cho Cloud.  

<img width="1067" height="444" alt="Image" src="https://github.com/user-attachments/assets/2f34d07a-594e-49fc-804b-bf2cf631d3d0" />   

   #### *b.1. Lấy Kubenetes URL:*  
Để lấy được Kubenetes URL của Cluster mà chúng ta tạo ở bước 3, chạy đoạn command sau:  

```gcloud container clusters describe <Tên Cluster> --zone=<Tên vùng> --format="value(endpoint)"```  

Kết quả hiện ra sẽ ở dưới dạng như 34.124.333.33 thì giá trị để điền vào ô Kubenetes URL sẽ là: ```https://34.124.333.33```  

   #### *b.2. Kubernetes server certificate key:*  

Chạy command sau:  

```gcloud container clusters describe <Tên Cluster> --zone=<Tên vùng> --format="value(masterAuth.clusterCaCertificate)"```  

Copy dãy Certificate và paste vào phần Kubernetes server certificate key.  

   #### *b.3. Tạo Credential cho Jenkins Cloud:*  
Để tạo Credential cho Jenkins Cloud kết nối tới Cluster, đầu tiên truy cập lại GCP https://console.cloud.google.com và chọn đúng project đang có Cluster.  
Tiến hành tạo Service Account (*Service Account dùng để truy cập vào các nền tảng khác như Kubenetes thay vì đăng nhập bằng tài khoản Google bình thường* ), vào IAM & Admin --> Service Accounts --> CREATE SERVICE ACCOUNT --> Đặt tên cho Service Account --> Done.  

<img width="1050" height="594" alt="Image" src="https://github.com/user-attachments/assets/5a33d119-fcb0-4bfe-b92d-38afa63dd736" />  
<img width="927" height="130" alt="Image" src="https://github.com/user-attachments/assets/85c6280d-8016-4a6c-ba3d-f5714c9bc3e4" />  
<img width="547" height="488" alt="Image" src="https://github.com/user-attachments/assets/70aff664-a4d6-4fc2-9383-3831727b4de6" />  

Tiếp theo chúng ta gán thêm quyền truy cập Kubenetes cho Service Account vừa tạo, vào IAM --> Grant Access  

<img width="816" height="295" alt="Image" src="https://github.com/user-attachments/assets/ddb3e6b7-ab2b-41a5-bd83-7876eff13eb5" />  

Bảng Grant Access hiện lên, điền các thông tin theo thứ tự sau:  
1. <tên service account>@<tên project>.iam.gserviceaccount.com  
2. Phần Assign Role chọn option Kubernetes Engine Admin.  
3. Thêm Assign Role chọn option Kubernetes Engine Cluster Admin. 

<img width="935" height="613" alt="Image" src="https://github.com/user-attachments/assets/0d7d62c2-35f0-4cf5-9ab9-16cd782b660f" />  

Xong nhấn Save để hoàn thành thêm quyền.  

Trở lại về Service Account vừa tạo, click vào Service Account đó và chuyển sang tab Key ở bên cạnh và chọn Add Key --> Create New Key --> Tích chọn Json --> nhấn Create và file Json sẽ được tải xuống.  

<img width="1203" height="540" alt="Image" src="https://github.com/user-attachments/assets/b56a43b4-b340-465a-aa48-c61544537447" />  

<img width="761" height="461" alt="Image" src="https://github.com/user-attachments/assets/9219ab02-554d-4bcd-a464-85bf65feb1b5" />  

Tiếp theo tiến hành lấy Access Token đại diện cho Servie Account, chạy command sau:  

```gcloud auth activate-service-account <tên service account>@<tên project>.iam.gserviceaccount.com --key-file=<Path chứa Json Key vừa tải>```  
```gcloud auth print-access-token```  
Đoạn Access Token sẽ được hiển thị như sau, Copy và lưu lại.  

<img width="1009" height="209" alt="Image" src="https://github.com/user-attachments/assets/0589cfc4-ffbb-4764-9b22-28ef334ec8fb" />  

Trở lại với Jenkins, kéo xuống phần Credential của giao diện New Cloud, Chọn Add --> Jenkins  

<img width="1141" height="340" alt="Image" src="https://github.com/user-attachments/assets/88bbaa9e-2267-4dd8-b3c7-266e46ebb58a" />  

Giao diện Add Credential hiện lên, điền các thông tin như sau:  
1. Để kind là Secret Text  
2. Paste Access Token ban nãy vừa lưu lại.  
3. Điền ID để quản lý.  
Xong chọn Save để hoàn thành.  

<img width="936" height="500" alt="Image" src="https://github.com/user-attachments/assets/e8b40924-a76a-4f38-82fb-ef19dce7895a" />  

Quay trở lại chỗ Credential và chọn đúng ID của Credential vừa tạo. Xong ấn "Test Connection" để xem đã kết nối được với Cluster chưa, nếu hiển thị như trong hình tức là đã kết nối thành công, xong nhấn "Save" để hoàn thành tạo Cloud kết nối Jenkins với Cluster. 

<img width="1112" height="195" alt="Image" src="https://github.com/user-attachments/assets/4c7a21e9-f15e-4a2c-a540-70935972ef90" />  

<img width="1221" height="259" alt="Image" src="https://github.com/user-attachments/assets/7535e086-2179-4eae-bf6e-f35edffd9035" />  

## 8. Khởi tạo luồng Jenkins CICD

### a. Lấy Github Access Token:  

Jenkins cần có Github Access Token để có thể trigger (nhận biết) vào từng Branch (nhánh) của Github để nhận biết Jenkinsfile. Trước hết lấy Github Access Token bằng cách click vào Avatar Github --> Setting --> Developer Settings

<img width="994" height="550" alt="Image" src="https://github.com/user-attachments/assets/16086200-a4e0-4e42-92b9-d76216115eaf" />  

Vào Personal Access Token --> Token Classic --> Generate new token --> Generate new token (Classic)  

<img width="1055" height="376" alt="Image" src="https://github.com/user-attachments/assets/ced75b73-7167-4182-b9b0-3ff77d91106c" />  
<img width="1039" height="358" alt="Image" src="https://github.com/user-attachments/assets/421a5b4e-f7c9-4e86-95f5-038be15d5b78" />  

Điền tên cho Github Access Token và chọn ngày hết hạn. Phần "Select Scope" có thể tích hết các Option.  

<img width="916" height="548" alt="Image" src="https://github.com/user-attachments/assets/05561388-82de-4963-9f94-e6be9dcb1b75" />  

Hoàn thành xong kéo xuống nhấn "Generate Token" để tạo Github Access Token. Giao diện chứa mã Github Access Token hiện lên. Tiến hành lưu mã Github Access Token ở nơi khác. Vì nếu mất không thể có lại được nữa.  

<img width="1010" height="444" alt="Image" src="https://github.com/user-attachments/assets/13852c0f-f9e8-4379-822e-d24b9443e881" />

### b. Thiếp lập thông tin trong Jenkinsfile: 

<img width="942" height="234" alt="Image" src="https://github.com/user-attachments/assets/92ed68dc-1a7b-4012-b80b-ef3b2834e662" />  

Một số thông tin phải thiết lập ở trong file Jenkinsfile, mục (1) là Repository hiện đang có trên Dockerhub, phải ở chế độ Public.   

Mục (2) là ID của Dockerhub Credential được tạo ở bước 7a, trong trường hợp này là "docker-credential".  

<img width="991" height="405" alt="Image" src="https://github.com/user-attachments/assets/d3158943-2c5b-4df5-a5b3-2ec71d9abf04" />  

Mục (3) là Credential của Cloud được tạo ở bước 7b.3  

Mục (4) là **Kubenetes URL** được tạo ra ở bước 7b.1  

<img width="1062" height="351" alt="Image" src="https://github.com/user-attachments/assets/f74d61c6-685e-434e-a32d-2edce5c6ba18" />  

### c. Thiết lập luồng CI/CD:  

Trở vè trang chủ Jenkins, chọn New Item.  

<img width="1144" height="349" alt="Image" src="https://github.com/user-attachments/assets/2ca9d739-ebee-4085-a960-af5425bb23e7" />  

Đặt tên cho Pipeline và chọn Multibranch Pipeline để quét toàn bộ các branch trong GitHub repo, xong nhấn OK.  

<img width="898" height="550" alt="Image" src="https://github.com/user-attachments/assets/1d26b847-bbdf-4626-b194-1b54c217f18d" />  

Giao diện General hiện lên. Điền tên Display Name, đây sẽ là tên hiển thị của luồng CI/CD.  
Kéo xuống ở phần Branch Source chọn Github, để Jenkins có thể xét toàn bộ các nhánh của Github Repo.  

<img width="897" height="486" alt="Image" src="https://github.com/user-attachments/assets/4dc4d976-37b0-46d6-92b4-3a374aa059eb" />  

Lập tức Github Credential hiện lên, chọn Add --> Chọn đúng tên Pipeline setup ban đầu.  

<img width="930" height="472" alt="Image" src="https://github.com/user-attachments/assets/dedac827-6b70-48f1-978f-25a60eb66b13" />  

Bảng Add Credential hiện lên. Điền các thông tin lần lượt như sau: 
1. Điền User name.             
2. Điền Github Access Token vào.  
3. Điền ID để quản lý.

<img width="963" height="491" alt="Image" src="https://github.com/user-attachments/assets/de53b89d-49c4-450d-a9ae-4c222b94021f" />  

Hoàn thiện xong nhấn Add. Quay trở lại giao diện Github Credential chọn đúng ID Credential vừa tạo **(1)**. Ở mục Repository HTTPS URL dán link của Github Repo vào **(2)**. Xong ấn Validate để kiểm tra kết nối **(3)**. Hiển thị "Credential OK" nghĩa là kết nối giữa Jenkins và Github Repo đã thành công. Xong nhấn   

<img width="888" height="406" alt="Image" src="https://github.com/user-attachments/assets/db62c007-64c7-4b46-a188-48b1242a1db7" />  

Xong nhấn "Save" để hoàn thiện xây dựng luồng CI/CD. Ngay khi ấn Save xong Jenkins sẽ quyét toàn bộ Github Repo, ở nhánh nào nếu có file Jenkinsfile thì Jenkins sẽ thực hiện các Stage và Step ( các giai đoạn và các bước ) đúng như trong file Jenkinsfile đề ra.  
Như trong hình, Jenkins đã quét ra được 1 file Jenkinsfile ở nhánh Main trong Github Repo.  

<img width="682" height="524" alt="Image" src="https://github.com/user-attachments/assets/dc6eee33-77e1-4008-ad8e-d2da6754adcc" />  

Vì Github Repo và Jenkins đã được trigger với nhau thông qua Webhook API ( ngrok ) nên Jenkins luôn tự động xem xét tìm kiếm Jenkinsfile ở trên mọi nhánh của Github Repo mỗi khi có Commit dưới local đẩy lên. Vì thế luồng tự động CI/CD được triển khai luôn ngay sau khi Pipeline (đoạn New Item) được tạo ra.  
Để theo dõi quá trình Jenkins thực thi, click vào tên Pipeline --> main --> Click vào số "1" ( Số 1 là số lần Jenkins chạy, Muốn chạy lần nữa click vào Build Now )  

<img width="1314" height="257" alt="Image" src="https://github.com/user-attachments/assets/44fc635c-abdb-4230-b8cd-6a02309517fb" />  
<img width="996" height="227" alt="Image" src="https://github.com/user-attachments/assets/7e5b099c-c748-414e-9fb3-02393cb1274c" />  
<img width="665" height="412" alt="Image" src="https://github.com/user-attachments/assets/8867427a-0845-4fa4-8d66-5dba1f2a5531" />  

Sau khi ấn vào số "1" xong, chọn "Console Output" để xem quá trình chạy của Jenkins.  

<img width="962" height="572" alt="Image" src="https://github.com/user-attachments/assets/d48438df-c6e0-4cdd-866b-d22d023b6ba2" />  

Hiển thị như trong hình nghĩa là luồng Jenkins đã chạy thành công trong việc triển khai 1 file deployment.yaml có 3 pod ( Replica=3 ) lên Cluster. *Nếu luồng chạy bị fail ở đoạn Deploy GKE thì hãy làm lại từ bước 7.b.3*  

<img width="1212" height="596" alt="Image" src="https://github.com/user-attachments/assets/38c4313c-1009-498c-833a-8eba84c10f89" />  

### d. Check kết quả API trả về:  

Check các Pod của file deployment.yaml được triển khai thành công: ```kubectl get pod -o wide```  

Như trong hình ta thấy hiện có 4 Pod, 3 Pod thuộc được Jenkins triển khai và 1 pod Jaeger nằm trong 3 Node của Cluster.  

<img width="985" height="238" alt="Image" src="https://github.com/user-attachments/assets/09d0ddd6-d279-42ea-9d0b-8e9b9a85d85c" />  

Service của deployment khi Jenkins triển khai là Node Port nên đê truy cập được vào service, chúng ta cần External IP của Node, chạy lệnh: ```kubectl get node -o wide``` và lấy External IP của 1 Node bất kỳ.  

<img width="977" height="155" alt="Image" src="https://github.com/user-attachments/assets/c4092aee-fa83-4970-94d8-4b015999ef1d" />  

Sau đó truy cập ```<External-IP-Node>:<nodePort của Service>/docs``` để vào Fast API của App. Giao diện hiện ra như trong ảnh tức Service đã triển khai thành công.  

<img width="1011" height="488" alt="Image" src="https://github.com/user-attachments/assets/a8ccd6e9-a698-49fe-a9b7-240e221dccf5" />  

Trước khi chạy thử, đầu tiên chúng ta cần lấy 1 trường hợp bất kỳ trong Datatable chứa 45000 trường hợp vay vốn. Mở file ML_DL_Loan_Deal_Classification.ipynb trong Folder jupyter-notebook-model, kéo xuống mục số 7 và copy dãy 14 số trong hình, bỏ số 0 ở cuối vì đây là Target Label ( 0 là vỡ nợ, 1 là trả được nợ ), đây chính là 13 feature được dùng đẻ train cho mô hình.    

<img width="1269" height="499" alt="Image" src="https://github.com/user-attachments/assets/9805f82e-8878-46f3-b485-a9aa09139b7c" />  

Quay trở lại với FAST API, chọn Post/predict --> Try it out --> Paste dãy số Feature  

<img width="1279" height="578" alt="Image" src="https://github.com/user-attachments/assets/e0286e5f-ac22-4bbe-9411-0137bcabab00" />  

Xong ấn Execute để gửi Request tới Model, kéo xuống dưới và thấy hiển thị như trong hình nghĩa là thành công response (đáp lại) cho request và kết quả trả về là 0 ( vỡ nợ ), đúng với kết quả Target Label của bài.  

<img width="1266" height="516" alt="Image" src="https://github.com/user-attachments/assets/62339e71-a1de-4597-a915-ae2ae88ce27e" />  

## **9. Các hệ thống giám sát:**  

### a. Prometheus:  

Để cài Prometheus, trước hết đảm bảo đã kết nối tới Cluster:  

```gcloud container clusters get-credentials <Tên Cluster> --zone <Vị trí đặt máy> --project <Tên dự án>```  

Tiến hành tạo 1 một kho lưu trữ Helm (Helm repository) tên là prometheus-community, chứa các Helm Chart (Grafana, prometheus,...) từ https://prometheus-community.github.io/helm-charts :  

```helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update```  

Để tạo 1 khu vực riêng biệt cho các Pod và service từ Helm, chúng ta tạo 1 Namespace ( khu vực ) riêng biệt tên là monitoring: ```kubectl create namespace monitoring```  

Cài đặt ứng dụng Prometheus vào cụm Cluster từ bộ kube-prometheus-stack trong Helm Repo prometheus-community với cấu hình của file prometheus-values.yaml  : ```helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --values prometheus/prometheus-values.yaml --wait```   

Hoàn thiện xong, kiểm tra các Pod và service:  

```kubectl get po -n monitoring - o wide```  
```kubectl get svc -n monitoring```  

<img width="993" height="194" alt="Image" src="https://github.com/user-attachments/assets/e063e5f6-4ab7-43fa-ae92-242e18ca0b99" />  

Chạy file service-monitor.yaml, Service Monitor có nhiệm vụ tự động phát hiện các Service ( thông qua gắn Match Label ) trong Cluster và cấu hình Prometheus để thu thập metrics từ các Service đó:  

 ```kubectl apply -f prometheus/service-monitor.yaml```  

Để vào Prometheus, chúng ta cần truy cập vào service tên là "prometheus-kube-prometheus-prometheus" thông qua Port-forward:  

```kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090```  

Truy cập service Prometheus bằng cách vào ```localhost:9090``` ,giao diện hiện lên như dưới nghĩa là vào Prometheus thành công:  

<img width="1312" height="481" alt="Image" src="https://github.com/user-attachments/assets/dbd84a4b-7bbb-4b46-b24e-11c520fb7a4f" />  

Để check Prometheus đã nhận biết và callout Metric từ Container ở Các Pod hay chưa, chúng ta vào Status --> Target Health  

<img width="883" height="468" alt="Image" src="https://github.com/user-attachments/assets/f870a44b-5705-42df-a2c1-1a1bcd2535c0" />  

Nếu thấy tên của service monitor như này nghĩa là Prometheus đã nhận biết được các Metric.  

<img width="1240" height="270" alt="Image" src="https://github.com/user-attachments/assets/0c93c73a-da1e-44af-94b9-66959f07be04" />  
<img width="941" height="263" alt="Image" src="https://github.com/user-attachments/assets/7dd2d777-af69-4f0b-ac73-6965c00ceffe" />  

Ở trong file ML-app.py đã được định nghĩa 3 Metric lần lượt như sau:  

<img width="842" height="347" alt="Image" src="https://github.com/user-attachments/assets/86bf1fd2-4a4b-4701-8cc2-f8d64c4a4b6e" />  

1. Metric tên là model_request_total: dạng counter, đếm số request được gửi tới Model, cả các request bị lỗi
2. Metric tên là ml_prediction_duration_seconds: dạng historgram, đo thời gian thực hiện request
3. Metric tên là ml_errors_total: dạng counter, đếm số request bị lỗi gửi tới Model

Gửi vài request tới Model, search ```model_request_total``` sẽ có được số request nhận được ở mỗi Pod.  

<img width="1312" height="369" alt="Image" src="https://github.com/user-attachments/assets/6b534b09-49ad-4175-9669-fa91e106b270" />  

Nếu search ```rate(model_request_total[6m]) * 6 *60``` chúng ta sẽ nhận được số request **trung bình** nhận được ( từ 1 giây nhận được bao nhiêu Request rồi nhân lên 6 phút ) ở mỗi Pod trong 6 phút gần nhất. Từ đó có thể thấy Pod loan-prediction-deployment-5b54876b5-lcp49 được phân bố nhận request nhiều nhất.  

<img width="1312" height="369" alt="Image" src="https://github.com/user-attachments/assets/afc9cbb8-c990-4725-a00c-3a67c2fb4193" />  

Tương tự vậy, gửi 1 số request lỗi đầu vào, như sai định dạng đầu vào để xem metric ml_error_total hoạt động như nào. Trong đó lỗi dạng ValueError là sai định dạng Input, lỗi HTTP là lỗi trả về API endpoint.  

<img width="1311" height="411" alt="Image" src="https://github.com/user-attachments/assets/2f2669dc-a250-4d73-b845-0bb8ef8a5f10" />  

Search metric ```ml_prediction_duration_seconds_sum``` ta sẽ được tổng thời gian xử lý các request, kể cả các request bị lỗi, từ lúc hoạt động tới hiện tại của mỗi Pod.  

<img width="1312" height="555" alt="Image" src="https://github.com/user-attachments/assets/b86eb471-4dd6-45f0-abf0-d45b27089534" />  

Search ```increase(ml_prediction_duration_seconds_sum[5m])``` sẽ nhận được tổng thời gian xử lý tất cả các request trong 5 phút gần nhất của mỗi Pod.  
Search ```ml_prediction_duration_seconds_count``` sẽ nhận được tổng số request nhận được ở mỗi Pod từ lúc khởi động tới hiện tại.  

<img width="1312" height="301" alt="Image" src="https://github.com/user-attachments/assets/8acf5213-ff07-40e5-ba55-2049d685337d" />  

### b. Grafana:  

Vì service của Grafana đã được triển khai ở bước trước nên nếu muốn truy cập vào Grafana, chúng ta chỉ cần port-forward cho service "prometheus-grafana":  

<img width="996" height="214" alt="Image" src="https://github.com/user-attachments/assets/822e71ad-0d16-4473-ba79-26cf21563956" />  

Mở Terminal mới, Chạy command: ```kubectl port-forward svc/prometheus-grafana -n monitoring  3000:80``` xong truy cập ```localhost:3000``` để vào Grafana.   

Giao diện Grafana hiện lên ,tên account để đăng nhập là admin, password nằm ở trong file prometheus-values.yaml  

<img width="849" height="512" alt="Image" src="https://github.com/user-attachments/assets/5ef5e7a2-43d0-42db-b677-dad178097da5" />  
<img width="922" height="406" alt="Image" src="https://github.com/user-attachments/assets/3f2af9d3-cdd5-432e-8b77-f00c876ad344" />  


Đăng nhập xong, click vào Dashboard --> New --> New Dashboard --> Add Visualization --> Chọn "Prometheus" để bắt đầu tạo Dashboard thể hiện các metric từ Promtheus.  

<img width="1060" height="424" alt="Image" src="https://github.com/user-attachments/assets/df29f030-c17e-4f38-bda5-302b2037aad9" />  

Bảng Edit Panel hiện ra, search metric ở vị trí (1), luôn để ở chế độ Code, xong ấn Run Query (2) để bắt đầu thể hiện biểu đồ của metric đang search.  

<img width="999" height="587" alt="Image" src="https://github.com/user-attachments/assets/a04e655d-5e45-426a-8bbe-696a2e299a21" />  

Biểu đồ của metric "model_request_total" hiện lên với mỗi màu là một Pod riêng biệt thể hiện thời điểm nhận số lượng request tương ứng thời gian.  

<img width="992" height="313" alt="Image" src="https://github.com/user-attachments/assets/1a6afb74-2422-40b3-bfd3-47470e0c8a52" />  

Điền tên cho biểu đồ và chọn "Save Dashboard".  

<img width="500" height="418" alt="Image" src="https://github.com/user-attachments/assets/0f08ae8f-5f4e-4694-a167-e6b42d758b95" />  

Đặt tên Title, đây là tên của Dashboard lớn quản lý nhiều Dashboard nhỏ bên trong.    

<img width="1298" height="455" alt="Image" src="https://github.com/user-attachments/assets/f022e7de-cb0b-4db9-a235-23dcad19e573" />  

Dashboard lớn hiện lên gồm 1 bảng dashboard nhỏ bên trong như trong hình, muốn thêm dashboard nhỏ nữa --> chọn "add" --> Vizualization  

<img width="1318" height="620" alt="Image" src="https://github.com/user-attachments/assets/cf3c0bcf-1073-4173-a650-b8f4f8d57271" />  

Để tính được trung bình 1 request được xử lý bao nhiêu giây trong vòng 5 phút gần nhất, chúng ta lấy tổng số thời gian xử lý tất cả request trong 5 phút chia cho tổng số lượng các request được gửi đến trong 10 phút, công thức sẽ là ```rate(ml_prediction_duration_seconds_sum[5m])``` chia cho ```rate(ml_prediction_duration_seconds_count[5m])```.  

<img width="979" height="578" alt="Image" src="https://github.com/user-attachments/assets/5c38266f-6ebf-4bb0-9286-e9d6256824a0" />  

Xong ấn Save dashboard để cho vào Dashboard lớn.  

<img width="1319" height="571" alt="Image" src="https://github.com/user-attachments/assets/3d05103f-127a-4f4b-b8df-fe1864b82e71" />  

Để tạo 1 Dashboard nhỏ thể hiện mức độ Memory Usage (tiêu tốn RAM) của các Pod. Chúng ta dùng công thức metric sau: ```(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024``` với ```node_memory_MemTotal_bytes``` là tổng RAM của node (tính bằng bytes), ```node_memory_MemAvailable_bytes``` là RAM còn trống có thể sử dụng ngay (bytes), trừ đi cho nhau chúng ta ra được số RAM đang được sử dụng của Pod đó. Xong đặt tên **Memory Usage (RAM) of Pod** và ấn Save dashboard để đưa Dashboard này vào Dashboard lớn.  

<img width="1319" height="471" alt="Image" src="https://github.com/user-attachments/assets/7016b014-845c-4714-bc9d-ee0327f17282" />  

Để tạo 1 Dashboard nhỏ thể hiện mức độ CPU Usage của các Pod tính theo đơn vị %, sử dụng công thức metric sau: ```(1 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])))) * 100``` với node_cpu_seconds_total{mode="idle"} là Thời gian CPU ở trạng thái rảnh. Xong đặt tên **CPU Usage of Pods** và ấn Save dashboard để đưa Dashboard này vào Dashboard lớn.  

Tổng hợp lại Dashboard lớn sẽ bao gồm 4 bảng nhỏ như sau từ trái qua phải, từ trên xuống dưới như sau:

* Bảng 1: Thể hiện mức tiêu hao CPU của từng Pod
* Bảng 2: Thể hiện thời gian xử lý 1 request của từng Pod
* Bảng 3: Tổng request nhận được của từng Pod
* Bảng 4: Thể hiện mực độ tiêu hao RAM của từng Pod

<img width="1319" height="508" alt="Image" src="https://github.com/user-attachments/assets/c28b4168-814f-46b4-ab6a-6f4e843e24d1" />  

### c. Jaeger Tracing:

Ở bước 4 chúng ta dã triển khai sẵn Jaeger rồi nên giờ muốn truy cập Jarger chỉ cần vào localhost:16686. Giao diện hiện như trong hình dưới nghĩa là thành công.  

<img width="1319" height="562" alt="Image" src="https://github.com/user-attachments/assets/25c517b0-4769-453c-93f1-7128779ec5cd" />  

Ở phần Service nếu search thấy tên service là "ml-prediction-service" như trong file ML-app.py định nghĩa Resource cho cả Metric lẫn Tracing ( resource = Resource.create({SERVICE_NAME: "ml-prediction-service"}) ) thì nghĩa là Jaeger đã bắt được trace thành công từ ML-app.py. Chọn đúng tên Service và ấn Find trace. 

<img width="1315" height="562" alt="Image" src="https://github.com/user-attachments/assets/3a928e46-ae25-445c-aab6-733cc3ec6b1c" />  

Các request sẽ được hiện ra trong sơ đồ, ví dụ như trong đây là 7 request, mỗi request là 1 dấm chấm. Trục tung thể hiện hời gian xử lý (latency) của mỗi request, với đơn vị là milliseconds (ms), trục hoành thể hiện mỗi dấu chấm tròn thể hiện một request được gửi đến service ml-prediction-service tại một thời điểm cụ thể.  

<img width="1292" height="565" alt="Image" src="https://github.com/user-attachments/assets/1953cc46-afee-4eab-abd4-e6b555771134" />  

Click vào 1 trong 7 request bất kỳ ở dưới, chúng ta sẽ thấy được 1 request có tổng thời gian thực hiện 5,95 ms được Tracing chia làm 2 giai đoạn là model_loader chạy trong  42 u.s và predictor chạy trong 4,8 ms.  

<img width="1322" height="245" alt="Image" src="https://github.com/user-attachments/assets/0a0c9786-1eba-4576-adf0-4474d996e918" />  

Hệ thống bao gồm các bước xây dựng Model, triển khai Model bằng Jenkins lên hạ tầng GKE của Google Cloud kèm theo Observable System được vận hành thành công.  

                  ----**THANKS YOU FOR READING TILL HERE, GOOD LUCK !**----
