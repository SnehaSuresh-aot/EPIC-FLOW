package org.camunda.bpm.extension.hooks.listeners;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.lang3.StringUtils;
import org.camunda.bpm.engine.delegate.*;
import org.camunda.bpm.extension.hooks.listeners.data.Email;
import org.camunda.bpm.extension.hooks.listeners.data.TokenResponse;
import org.camunda.bpm.extension.hooks.services.IMessageEvent;
import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormat;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.Base64Utils;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import javax.inject.Named;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import static org.camunda.bpm.extension.commons.utils.VariableConstants.TEMPLATE;

@Named("CustomCommonEmailServiceListener")
public class CustomCommonEmailServiceListener extends BaseListener implements ExecutionListener, TaskListener, IMessageEvent {

    private final Logger LOGGER = Logger.getLogger(CustomCommonEmailServiceListener.class.getName());

    private WebClient webClient = null;

    private Expression currentDate;

    @Value("${ches.auth.tokenUri}")
    private String authTokenUri;

    @Value("${ches.reminderConfigurationUri}")
    private String reminderConfigurationUri;

    @Value("${ches.auth.clientId}")
    private String clientId;

    @Value("${ches.auth.clientSecret}")
    private String clientSecret;

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        sendEmail(execution);
    }

    @Override
    public void notify(DelegateTask delegateTask) {
        sendEmail(delegateTask.getExecution());
    }

    public void sendEmail(DelegateExecution execution) {
        try {
            webClient = setWebclient();

            Mono<ResponseEntity<String>> entityMono = webClient
                    .post()
                    .uri(reminderConfigurationUri)
                    .header(HttpHeaders.AUTHORIZATION, "Bearer " + getAccessToken())
                    .accept(MediaType.APPLICATION_JSON)
                    .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                    .bodyValue(getEmailData(execution))
                    .retrieve()
                    .toEntity(String.class);

            ResponseEntity<String> response = entityMono.block();
            LOGGER.info("Email Response : " + response);

        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private String getAccessToken() {
        webClient = setWebclient();

        String encodedClientData =

                Base64Utils.encodeToString(String.format(clientId + ":" + clientSecret).getBytes(StandardCharsets.UTF_8));

        TokenResponse response = webClient
                .post()
                .uri(authTokenUri)
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_FORM_URLENCODED_VALUE)
                .header("Authorization", "Basic" + " " + encodedClientData)
                .body(BodyInserters.fromFormData("grant_type", "client_credentials"))
                .retrieve()
                .bodyToMono(TokenResponse.class)
                .block();
        // LOGGER.info("Access Token : " + response.getAccess_token());
        return response.getAccess_token();



    }

    private WebClient setWebclient() {
        if (webClient == null) {
            return WebClient.builder()
                    .build();
        }
        return webClient;
    }

    private Email getEmailData(DelegateExecution execution) throws JsonProcessingException {
        Map<String, Object> dmnMap = getDMNTemplate(execution);
        ObjectMapper objectMapper = new ObjectMapper();
//        objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
//        Email email = objectMapper.convertValue(dmnMap, Email.class);

        Email email = new Email();
        List<String> toAddress = objectMapper.readValue(getDmnValue(dmnMap, "to"), List.class);
        email.setTo(toAddress);
        email.setFrom(getDmnValue(dmnMap, "from"));
        execution.setVariable("dueDate", getDueDate(execution));
        String emailBody = getDmnValue(dmnMap, "body");
        for(Map.Entry<String,Object> entry : execution.getVariables().entrySet()) {
            if(!TEMPLATE.equals(entry.getKey())) {
                emailBody = StringUtils.replace(emailBody,"@"+entry.getKey(), entry.getValue()+StringUtils.EMPTY);
            }
        }
        email.setBody(emailBody);
        LOGGER.info("Email Body : " + emailBody);
        email.setSubject(getDmnValue(dmnMap, "subject"));
        email.setBodyType(getDmnValue(dmnMap, "bodyType"));
        return email;
    }

    private Map<String, Object> getDMNTemplate(DelegateExecution execution) {
        return (Map<String, Object>) execution.getVariables().get(TEMPLATE);
    }

    private String getDueDate(DelegateExecution execution) {
        DateTime currentDate = this.currentDate != null && this.currentDate.getValue(execution) != null ?
                new DateTime(String.valueOf(this.currentDate.getValue(execution))) : new DateTime();
        DateTime dueDate = addBusinessDays(currentDate, 7);
        return  dueDate.toString(DateTimeFormat.fullDate());
    }

    private String getDmnValue(Map<String, Object> dmnMap, String name) {
        return String.valueOf(dmnMap.get(name));
    }

}
