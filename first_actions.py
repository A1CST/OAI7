import os
import subprocess
import init_setup  # Ensure init_setup.py is in the same directory

def main():
    required_files = ["sql_executor.py", "init_sql.py"]
    missing_files = [file for file in required_files if not os.path.exists(file)]

    if missing_files:
        print(f"Missing required files: {', '.join(missing_files)}")
        for file in missing_files:
            if file == "sql_connect.py":
                print("Calling function to create sql_connect.py...")
                init_setup.create_sql_executor()  # Assuming sql_connect.py is replaced by sql_executor.py
            elif file == "init_sql.py":
                print("Calling function to create init_sql.py...")
                ip_address = input("Enter your MySQL server IP address: ").strip()
                root_user = input("Enter your MySQL root username (default: root): ").strip() or "root"
                init_setup.create_user_and_database(ip_address, root_user)
    else:
        print("All required files are present. Running init_collections.py...")
        try:
            subprocess.run(['python', 'init_collections.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running init_collections.py: {e}")
        except FileNotFoundError:
            print("init_collections.py not found. Please ensure it is in the same directory.")

if __name__ == "__main__":
    main()
