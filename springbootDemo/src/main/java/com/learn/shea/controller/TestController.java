package com.learn.shea.controller;

import com.learn.shea.service.TestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RequestMapping("/test")
@RestController
public class TestController {

    @Autowired
    TestService testService;

    @GetMapping("/hello")
    public String helloWorld(){
        return "hello world";
    }
    @GetMapping("/test")
    public int test(){
        try {
            return testService.test();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return 0;
    }

}
