FROM logstash:latest

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json 

RUN logstash-plugin install logstash-output-kafka  

RUN chmod -R 777 /var/log/
