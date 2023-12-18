# Andre_Garcia-Veeam_challenge
 Email challenge proposed by Veeam for my job application.

 I have implemented the file comparison using the filecmp library. I am aware I could have used a hash function such as MD5 to compare files, however, this method's performance should be similar, as the hashification of the files can take a long time depending on the size of the file. In truth, the best solution would be to implement both approaches for each use case, but I assume most people will implement the MD5 version, as it is referred to on the exercise, so I decided to do this one instead.

 ## Use:
 Run the CLI command: python .\SuncProgram.py source_path=*add_source_here* replica_path=*add_replica_here* logs_path=*add_logs_here* sync_interval=*add_interval_here*

 The only required arguments are replica_path and logs_path, and the order is irrelevant. The local folder is the default source and 10 seconds is the default synchronization interval.
