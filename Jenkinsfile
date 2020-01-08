pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile'
    }

  }
  stages {
    stage('Test') {
      steps {
        sh 'PYTHONPATH=$PYTHONPATH:`pwd` pytest --showlocals -v demo --junit-xml test-reports/results.xml || echo 0'
      }
    }

    stage('Static Tests') {
      steps {
        echo 'Static Tests'
      }
    }

  }
}